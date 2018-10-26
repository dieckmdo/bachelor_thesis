/**
 * Copyright 2018 University of Bremen, Institute for Artificial Intelligence
 * Author(s): Dominik Dieckmann <dieckmdo@uni-bremen.de>
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
#include <uima/api.hpp>

#include <pcl/point_types.h>
#include <rs/types/all_types.h>

#include <opencv2/opencv.hpp>
//RS
#include <rs/scene_cas.h>
#include <rs/utils/time.h>
#include <rs/DrawingAnnotator.h>

using namespace uima;


class UnrealGTAnnotator : public DrawingAnnotator
{
private:
  std::string gtFilePath;
  cv::Mat color, objects, disp;
  std::map<std::string, cv::Vec3b> objectMap;
  std::map<std::string, std::string> gtMap;

  enum
  {
    objImage,
    gtImage,
  } dispMode;

public:

  UnrealGTAnnotator() : DrawingAnnotator(__func__), dispMode(gtImage) {}

  TyErrorId initialize(AnnotatorContext &ctx)
  {
    outInfo("initialize");

    ctx.extractValue("gtFilePath", gtFilePath);
    cv::FileStorage fs(gtFilePath, cv::FileStorage::READ);

    cv::FileNode fn = fs.root();
    for(cv::FileNodeIterator fit = fn.begin(); fit != fn.end(); ++fit)
    {
      cv::FileNode object = *fit;
      outInfo(object.name());
      gtMap.insert(std::pair<std::string, std::string>(object.name(), fs[object.name()]));
    }

    fs.release();
    return UIMA_ERR_NONE;
  }

  TyErrorId destroy()
  {
    outInfo("destroy");
    return UIMA_ERR_NONE;
  }

  TyErrorId processWithLock(CAS &tcas, ResultSpecification const &res_spec)
  {
    MEASURE_TIME;
    outInfo("process begins");

    rs::SceneCas cas(tcas);
    rs::Scene scene = cas.getScene();

    cas.get(VIEW_COLOR_IMAGE_HD, color);
    cas.get(VIEW_OBJECT_IMAGE_HD, objects);
    cas.get(VIEW_OBJECT_MAP, objectMap);

    disp = color.clone();

    std::vector<rs::Identifiable> cleanedClusters;

    std::vector<rs::Cluster> clusters;
    scene.identifiables.filter(clusters);

    outInfo("Found " << clusters.size() << " clusters");

    for(auto cluster : clusters)
    {
      cv::Rect roi;
      rs::conversion::from(cluster.rois.get().roi_hires.get(), roi);

      cv::Mat imageRoi = cv::Mat(objects, roi);

      // cv::Vec3b not a possible key, so using the name of the object associated with the color.
      std::map<std::string, int> colorCount;

      for(int r = 0; r < imageRoi.rows; ++r)
      {
        const cv::Vec3b *imageIt = imageRoi.ptr<cv::Vec3b>(r);

        for(int c = 0; c < imageRoi.cols; ++c, ++imageIt)
        {
          std::map<std::string, cv::Vec3b>::iterator objMapIt;

          // find entry in objectMap matching color
          for(objMapIt = objectMap.begin(); objMapIt != objectMap.end(); ++objMapIt)
          {
            if(objMapIt->second == *imageIt)
            {
              // add new object occurence to colorCount or increase value
              std::pair<std::map<std::string, int>::iterator, bool> countIt = colorCount.insert(std::pair<std::string, int>(objMapIt->first, 1));
              if(countIt.second == false)
              {
                ++countIt.first->second;
              }
            }
          }
        }
      }

      // for small objects, that do not have the most pixels in their roi (cutlery)
      for(int i = 0; i < 2; ++i)
      {
        if(colorCount.empty())
        {
          break;
        }

        std::string mostColor = getObjectWithMostOccurences(colorCount);

        if(mostColor == "SM_WindowTypARight1_12")
        {
          break;
        }

        //object names should follow Unreal Engine naming standard: SM_ObjectName_X
        //if that standard not given, the object does not belong to the experiment/the objects that should be annotated
        std::vector<std::string> objNameParts;
        boost::split(objNameParts, mostColor, boost::is_any_of("_"));
        if(objNameParts.size() < 3 || objNameParts[1].empty() || objNameParts[1] == "")
        {
          colorCount.erase(mostColor);
          continue;
        }

        auto foundObj = gtMap.find(objNameParts[1]);

        if(foundObj == gtMap.end())
        {
          colorCount.erase(mostColor);
        }
        else
        {
          rs::GroundTruth gt = rs::create<rs::GroundTruth>(tcas);
          rs::Classification classification = rs::create<rs::Classification>(tcas);
          classification.classification_type.set("ground_truth");
          classification.classname.set(foundObj->second);
          classification.classifier.set("UnrealEngine");
          classification.source.set("UnrealGTAnnotator");
          gt.classificationGT.set(classification);
          cluster.annotations.append(gt);

          cleanedClusters.push_back(cluster);

          drawResults(roi, foundObj->second);
          break;
        }
      }
    }

    outInfo("Reduced to " << cleanedClusters.size() << " clusters");
    scene.identifiables.set(cleanedClusters);

    //when running with multiple images and therefor with multiple objectMaps, the map gets expanded by the new occuring objects per image.
    //clearing the map prevents that
    objectMap.clear();

    return UIMA_ERR_NONE;
  }

  // find the most occuring color
  std::string getObjectWithMostOccurences(std::map<std::string, int> map)
  {
    std::map<std::string, int>::iterator mostColor = map.begin();
    for(std::map<std::string, int>::iterator it = map.begin(); it != map.end(); ++it)
    {
      if(it->second > mostColor->second)
      {
        mostColor = it;
      }
    }
    return mostColor->first;
  }


  void drawImageWithLock(cv::Mat &d)
  {
    switch(dispMode)
    {
      case objImage:
        d = objects.clone();
        break;
      default:
        d = disp.clone();
    }
  }

  void drawResults(cv::Rect roi,std::string gt)
  {
      cv::rectangle(disp,roi,cv::Scalar(200,0,0),2);
      int baseLine;
      cv::Size textSize = cv::getTextSize(gt ,cv::FONT_HERSHEY_PLAIN,1.5,2.0, &baseLine);
      cv::putText(disp, gt ,cv::Point(roi.x,roi.y-textSize.height), cv::FONT_HERSHEY_PLAIN, 1.5, CV_RGB(255, 20, 147), 2.0);
  }

  bool callbackKey(const int key, const Source source)
  {
    switch(key)
    {
    case 'g':
    case 'G':
      dispMode = gtImage;
      break;
    case 'o':
    case 'O':
      dispMode = objImage;
      break;
    }
    return true;
  }

};

// This macro exports an entry point that is used to create the annotator.
MAKE_AE(UnrealGTAnnotator)
