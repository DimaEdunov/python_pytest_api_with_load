import uuid
from enum import Enum


class AttractionParameters(Enum):

    ORIGIN_UUID = uuid.uuid1()

    DV_ATTRACTION_NAMES = ["CC", "DV"]
    TV_ATTRACTION_NAMES = ["TE", "TV"]
    CO_ATTRACTION_NAMES = ["CO", "CV"]
    TP_ATTRACTION_NAMES = ["SV", "VS"]
    TP_WV_ATTRACTION_NAMES = ["WV", "VW"]
    TP_AV_ATTRACTION_NAMES = ["SW", "AV"]
    NJ_ATTRACTION_NAMES = ["NJ", "NV"]
    PV_ATTRACTION_NAMES = ["PP", "PV"]
    LG_ATTRACTION_NAMES = ["MM", "VM"]
    LK_ATTRACTION_NAMES = ["LK", "LV"]
    BV_ATTRACTION_NAMES = ["BR", "BV"]
    JU_ATTRACTION_NAMES = ["JV", "VL"]
    LG_DV_ATTRACTION_NAMES = ["FD", "DV"]
    LG_NV_ATTRACTION_NAMES = ["NJ", "NV"]
    DM_BV_ATTRACTION_NAMES = ["BT", "BV"]
    DM_TV_ATTRACTION_NAMES = ["TT", "TV"]
    LL_DV_ATTRACTION_NAMES = ["CD", "DV"]
    LL_NV_ATTRACTION_NAMES = ["NJ", "NV"]
    LB_DV_ATTRACTION_NAMES = ["TD", "DV"]
    LB_NV_ATTRACTION_NAMES = ["NJ", "NV"]
    AQ_ATTRACTION_NAMES = ["ZV", "JJ"]
    FU_TO_ATTRACTION_NAMES = ["FU", "TO"]
    AV_TV_ATTRACTION_NAMES = ["TA", "TV"]
    AV_CV_ATTRACTION_NAMES = ["CB", "CV"]
    AV_WC_ATTRACTION_NAMES = ["WC", "WV"]
    AV_XV_ATTRACTION_NAMES = ["XT", "XV"]
    AV_FV_ATTRACTION_NAMES = ["FT", "FV"]
    AV_VV_ATTRACTION_NAMES = ["VI", "VV"]
    AV_GV_ATTRACTION_NAMES = ["GO", "GV"]
    DQ_BV_ATTRACTION_NAMES = ["BB", "BV"]
    DQ_SV_ATTRACTION_NAMES = ["SM", "SV"]
    DQ_GV_ATTRACTION_NAMES = ["GO", "GV"]
    DQ_IV_ATTRACTION_NAMES = ["IR", "IV"]
    DQ_RV_ATTRACTION_NAMES = ["RR", "RV"]
    DQ_WV_ATTRACTION_NAMES = ["WW", "WV"]
    DQ_CV_ATTRACTION_NAMES = ["CH", "CV"]
    AT_SV_ATTRACTION_NAMES = ["SV", "VS"]
    AT_WV_ATTRACTION_NAMES = ["WM", "WV"]
    AT_CV_ATTRACTION_NAMES = ["HH", "CV"]
    AT_NV_ATTRACTION_NAMES = ["NE", "NV"]
    AJ_GV_ATTRACTION_NAMES = ["GL", "GV"]
    AJ_NV_ATTRACTION_NAMES = ["NI", "NV"]
    AJ_KV_ATTRACTION_NAMES = ["KK", "KV"]
    AJ_EV_ATTRACTION_NAMES = ["ET", "EV"]
    AJ_MV_ATTRACTION_NAMES = ["MD", "MV"]
    AG_BV_ATTRACTION_NAMES = ["BM", "BV"]
    AG_MV_ATTRACTION_NAMES = ["MB", "MV"]
    AG_GV_ATTRACTION_NAMES = ["GO", "GV"]
    AG_LV_ATTRACTION_NAMES = ["GO", "LV"]
    TT_SV_ATTRACTION_NAMES = ["SB", "SV"]

    @staticmethod
    def video_test_status(key):
        test_status = {"old": "old_file_name_structure", "new": "new_file_name_structure"}
        return test_status[key]

    @staticmethod
    def get_folder_path(key):
        folder_path = {"dv": "\\media-testing\\LF-DV-(The-dragon)\\single_photo",
                       "LF-TV": "\\media-testing\\LF-TV-(The-Great-Lego-Race)\\single_photo_example_2",
                       "cv": "\\media-testing\\LF-CV-(Coastersaurus)\\single_photo",
                       "TP-SV": "\\media-testing\\TP-ST-(Stealth-Scream-Video)\\single_photo",
                       "TP-WV": "\\media-testing\\TP-TS-(Swarm)",
                       "TP-AV": "\\media-testing\\TP-AV-(Saw)",
                       "nj": "\\media-testing\\LF-NV-(Ninjago)",
                       "pv": "\\media-testing\\LF-PV-(Daddy-Pigs)",
                       "mv": "\\media-testing\\LG-MM-(Maximus)\\full_photo",
                       "lv": "\\media-testing\\LF-LK-(Lost-Kingdom-Adventure)",
                       "ju": "\\media-testing\\CH-JU-(Mandrill-Mayhem)\\single_photo",
                       "LG-DV": "\\media-testing\\LG-DV-(Fire-Dragon)\\full_photo",
                       "LG-NV": "\\media-testing\\LG-NV-(Ninjago)",
                       "DM-BV": "\\media-testing\\DM-BV(Accelerator)",
                       "DM-TV": "\\media-testing\\DM-TV-(Troublesome-Trucks)",
                       "LB-DV": "\\media-testing\\LB-DV(The-Dragon)",
                       "LB-NV": "\\media-testing\\LB-NV(Ninjago-The-Ride)",
                       "LL-DV": "\\media-testing\\LL-DV-(The-Dragon)",
                       "LL-NV": "\\media-testing\\LL-NV-(Ninjago-The-Ride)",
                       "hh": "\\media-testing\\hh",
                       "aq": "\\media-testing\\test",
                       "FU-TO": "\\media-testing\\FU-TO-(Futuroscope)",
                       "EF-BV": "\\media-testing\\EF-BV-(Efteling)\\single_photo",
                       "AV-TV": "\\media-testing\\AV-TV-(Tatsu)\\full_photo",
                       "AV-CV": "\\media-testing\\AV-CV-(Canyon-Blaster)\\single_photo",
                       "AV-WV": "\\media-testing\\AV-WV-(West-Coaster-Racers)",
                       "AV-XV-left": "\\media-testing\\AV-XV-(X2-left)\\test",
                       "AV-XV-right": "\\media-testing\\AV-XV-(X2-right)\\full_photo",
                       "AV-FV": "\\media-testing\\AV-FV-(Full-Throttle)",
                       "AV-VV": "\\media-testing\\AV-VV-(Viper)",
                       "AV-GV": "\\media-testing\\AV-GV-(Goliath)",
                       "DQ-BV": "\\media-testing\\DQ-BV-(Bugs-Bunny-White-Water-Rapids)",
                       "DQ-CV-left": "\\media-testing\\DQ-CV-(Cliffhanger-011-left)",
                       "DQ-CV-right": "\\media-testing\\DQ-CV-(Cliffhanger-012-right)",
                       "DQ-SV": "\\media-testing\\DQ-SV-(Superman)",
                       "DQ-GV-left": "\\media-testing\\DQ-GV-(Goliath-left)",
                       "DQ-GV-right": "\\media-testing\\DQ-GV-(Goliath-right)",
                       "DQ-IV": "\\media-testing\\DQ-IV-(Iron-Rattler)",
                       "DQ-RV": "\\media-testing\\DQ-RV-(Road-Runner)\\single_photo",
                       "DQ-WV": "\\media-testing\\DQ-WV-(Wonder-Woman)",
                       "AT-SV": "\\media-testing\\AT-SV-(Alton-Towers-Resort)\\single_photo",
                       "AT-WV": "\\media-testing\\AT-WV-(Wickerman)",
                       "AT-CV": "\\media-testing\\AT-CV-(Curse-of-Alton-Manor)",
                       "AT-NV-left": "\\media-testing\\AT-NV-(Nemesis-left)",
                       "AT-NV-right": "\\media-testing\\AT-NV-(Nemesis-right)",
                       "AJ-GV": "\\media-testing\\AJ-GV-(Green-Lantern)",
                       "AJ-NV": "\\media-testing\\AJ-NV-(Nitro)",
                       "AJ-SV": "\\media-testing\\AJ-SV-(Superman)",
                       "AJ-KV": "\\media-testing\\AJ-KV-(Kingda-Ka)",
                       "AJ-EV": "\\media-testing\\AJ-EV-(El-Toro)\\single_photo",
                       "AJ-MV": "\\media-testing\\AJ-MV-(Medusa)\\single_photo",
                       "AG-TV": "\\media-testing\\AG-TV-(Twisted-Cyclone)",
                       "AG-MV": "\\media-testing\\AG-MV-(THE-RIDDLER-Mindbender)",
                       "AG-GV": "\\media-testing\\AG-GV-(Goliath)\\single_photo",
                       "AG-LV": "\\media-testing\\AG-LV(Log-Jamboree)",
                       "TT-SV-left": "\\media-testing\\TT-SV-(Beams-left)\\full",
                       "TT-SV-right": "\\media-testing\\TT-SV-(Beams-right)"}

        return folder_path[key]

    @staticmethod
    def media_meta_data(key):
        media_meta_data = {
            "dq_meta_data": f'{{"syncTimeArray":[0.671,0.879,1.076,1.27,1.466,1.651],"cameraAngle":30,"roiArray":[{{"height":200,"name":"People","width":200,"x":10,"y":10}}],"originUUID":"{AttractionParameters.ORIGIN_UUID.value}","parentUUID":"5296fc80-b23d-11ee-9b5c-950a055deb6c"}}',
            "origin_uuid": AttractionParameters.ORIGIN_UUID.value}
        return media_meta_data[key]
