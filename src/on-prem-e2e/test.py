import json

# Original JSON string
original_json = '''{
 "pk": "domain#aj#att#kv",
 "sk": "service#mediaEditor#configurationId#kingda_ka_img_prt",
 "attraction": "kv",
 "configurationId": "kingda_ka_img_prt",
 "domain": "aj",
 "edl": {
  "height": 1920,
  "outputs": {
   "bucket": "${outputs.bucket}",
   "filename": "${outputs.main.name}.jpg",
   "localPath": "${outputs.main.localpath}",
   "path": "${outputs.main.path}",
   "storage": "gc",
   "subProducts": [
    {
     "filename": "${outputs.wm.name}.jpg",
     "source": {
      "bucket": "config.pomvom.com",
      "name": "WM-6F-1080-1920",
      "path": "${genericWatermark}/WM-6F-1080-1920.png",
      "storage": "s3",
      "type": "watermark"
     },
     "type": "wm"
    },
    {
     "filename": "${outputs.main.name}_small.jpg",
     "of": "${outputs.main.name}.jpg",
     "type": "small"
    },
    {
     "filename": "${outputs.wm.name}_small.jpg",
     "of": "${outputs.wm.name}.jpg",
     "type": "small"
    },
    {
     "filename": "${outputs.wm.name}_medium.jpg",
     "of": "${outputs.wm.name}.jpg",
     "type": "small"
    },
    {
     "filename": "${outputs.main.name}_medium.jpg",
     "of": "${outputs.main.name}.jpg",
     "type": "small"
    },
    {
     "filename": "thumb.jpg",
     "type": "thumb"
    }
   ],
   "type": "image"
  },
  "scenes": [
   {
    "layers": [
     {
      "layerNumber": 1,
      "source": {
       "bucket": "config.pomvom.com",
       "name": "black_solid_portrait",
       "path": "${genericParkPath}/black_solid_portrait.jpg",
       "storage": "s3",
       "type": "visual"
      }
     },
     {
      "keyFrames": {
       "filters": [
        {
         "effectDuration": 1,
         "rotationAngleEnd": -10,
         "rotationAngleStart": -10,
         "scaleFactorIn": 1.05,
         "scaleFactorOut": 1.05,
         "zoomToXIn": 430,
         "zoomToXOut": 430,
         "zoomToYIn": 200,
         "zoomToYOut": 200
        }
       ]
      },
      "layerNumber": 1,
      "source": {
       "name": "raw1",
       "type": "user"
      }
     },
     {
      "fitTo": {
       "height": 1920,
       "topLeft": {
        "x": 0,
        "y": 0
       },
       "width": 1080
      },
      "layerNumber": 2,
      "source": {
       "bucket": "config.pomvom.com",
       "name": "GA_STORY_KIINGDA-KA",
       "path": "${genericAttractionPath}/GA_STORY_KIINGDA-KA.png",
       "storage": "s3",
       "type": "visual"
      }
     }
    ]
   }
  ],
  "width": 1080
 },
 "env": {
  "genericAttractionPath": "us/aj/video/kv/kingda_ka_img_prt",
  "genericParkPath": "us/aj/video/generic_sixflag",
  "genericWatermark": "us/generic/watermarks"
 },
 "mediaTags": [
  "image_portrait"
 ],
 "outputMediaExtension": "jpg",
 "outputMediaType": "Image",
 "service": "mediaEditor",
 "_ct": "2023-10-16T14:53:39.252Z",
 "_et": "ClipGeneratorConfiguration",
 "_md": "2023-10-16T14:53:39.252Z"
}'''

# Copied JSON string
copied_json = '''{
    "outputMediaType": "Image",
    "mediaTags": [
        "image_portrait"
    ],
    "configurationId": "kingda_ka_img_prt",
    "_et": "ClipGeneratorConfiguration",
    "env": {
        "genericWatermark": "us/generic/watermarks",
        "genericAttractionPath": "us/aj/video/kv/kingda_ka_img_prt",
        "genericParkPath": "us/aj/video/generic_sixflag"
    },
    "edl": {
        "width": 1080,
        "outputs": {
            "bucket": "${outputs.bucket}",
            "path": "${outputs.main.path}",
            "subProducts": [
                {
                    "type": "wm",
                    "filename": "${outputs.wm.name}.jpg",
                    "source": {
                        "bucket": "config.pomvom.com",
                        "name": "WM-6F-1080-1920",
                        "path": "${genericWatermark}/WM-6F-1080-1920.png",
                        "storage": "s3",
                        "type": "watermark"
                    }
                },
                {
                    "type": "small",
                    "filename": "${outputs.main.name}_small.jpg",
                    "of": "${outputs.main.name}.jpg"
                },
                {
                    "type": "small",
                    "filename": "${outputs.wm.name}_small.jpg",
                    "of": "${outputs.wm.name}.jpg"
                },
                {
                    "type": "small",
                    "filename": "${outputs.wm.name}_medium.jpg",
                    "of": "${outputs.wm.name}.jpg"
                },
                {
                    "type": "small",
                    "filename": "${outputs.main.name}_medium.jpg",
                    "of": "${outputs.main.name}.jpg"
                },
                {
                    "type": "thumb",
                    "filename": "thumb.jpg"
                }
            ],
            "filename": "${outputs.main.name}.jpg",
            "localPath": "${outputs.main.localpath}",
            "storage": "gc",
            "type": "image"
        },
        "scenes": [
            {
                "layers": [
                    {
                        "layerNumber": 1,
                        "source": {
                            "bucket": "config.pomvom.com",
                            "name": "black_solid_portrait",
                            "path": "${genericParkPath}/black_solid_portrait.jpg",
                            "storage": "s3",
                            "type": "visual"
                        }
                    },
                    {
                        "layerNumber": 1,
                        "keyFrames": {
                            "filters": [
                                {
                                    "rotationAngleEnd": -10,
                                    "zoomToYOut": 200,
                                    "scaleFactorOut": 1.05,
                                    "zoomToXOut": 430,
                                    "zoomToYIn": 200,
                                    "rotationAngleStart": -10,
                                    "zoomToXIn": 430,
                                    "scaleFactorIn": 1.05,
                                    "effectDuration": 1
                                }
                            ]
                        },
                        "source": {
                            "name": "raw1",
                            "type": "user"
                        }
                    },
                    {
                        "layerNumber": 2,
                        "fitTo": {
                            "width": 1080,
                            "height": 1920,
                            "topLeft": {
                                "x": 0,
                                "y": 0
                            }
                        },
                        "source": {
                            "name": "GA_STORY_KIINGDA-KA",
                            "bucket": "config.pomvom.com",
                            "path": "${genericAttractionPath}/GA_STORY_KIINGDA-KA.png",
                            "storage": "s3",
                            "type": "visual"
                        }
                    }
                ]
            }
        ],
        "height": 1920
    },
    "_ct": "2023-10-16T14:53:39.252Z",
    "service": "mediaEditor",
    "attraction": "kv",
    "_md": "2023-10-16T14:53:39.252Z",
    "sk": "service#mediaEditor#configurationId#kingda_ka_img_prt",
    "outputMediaExtension": "jpg",
    "pk": "domain#aj#att#kv",
    "domain": "aj"
}'''

# Load the JSON strings into Python dictionaries
original_data = json.loads(original_json)
copied_data = json.loads(copied_json)


# Function to compare two JSON objects and report differences
def compare_json(obj1, obj2, path=""):
    print("XXXX")
    if isinstance(obj1, dict) and isinstance(obj2, dict):
        for key in obj1:
            if key not in obj2:
                print(f"Key {path + '/' + key} missing in copied JSON")
            else:
                compare_json(obj1[key], obj2[key], path + '/' + key)
        for key in obj2:
            if key not in obj1:
                print(f"Key {path + '/' + key} missing in original JSON")
    elif isinstance(obj1, list) and isinstance(obj2, list):
        for index, (item1, item2) in enumerate(zip(obj1, obj2)):
            compare_json(item1, item2, path + f'[{index}]')
        if len(obj1) != len(obj2):
            print(f"Lists differ in length at {path}")
    else:
        if obj1 != obj2:
            print(f"Difference at {path}: {obj1} != {obj2}")


# Compare the two JSON objects and print differences
compare_json(original_data, copied_data)
