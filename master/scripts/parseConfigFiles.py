import xml.etree.ElementTree as ET
import glob
import os
import re
import base64
import sys
from scripts.pp7_pb2 import presentation_pb2


def ParseConfigFiles(config_manager):
    ParseMasterConfigPro6(config_manager)
    ParseMasterConfigPro7(config_manager)
    ParseConfigFilesPro6(config_manager)
    ParseConfigFilesPro7(config_manager)
    if (len(config_manager["fileConfigs"]) == 0) and (len(config_manager["fileConfigs7"]) == 0):
        raise ValueError(
            'Error: No configuration file was found in sub folders')


def ParseMasterConfigPro6(config_manager):
    print('Parsing "masterConfig_Groups.pro6"')
    config_manager["groupConfigs"] = {}
    __file = __file__.decode(sys.getfilesystemencoding())
    dirname = os.path.dirname(os.path.abspath(__file))
    parent_parent_dir = os.path.abspath(os.path.join(os.path.join(dirname, os.pardir), os.pardir))
    try:
        tree = ET.parse(os.path.join(parent_parent_dir, "config", "masterConfig_Groups.pro6"))
    except:
        raise ValueError(
            'Error: "masterConfig_Groups.pro6" was not found in master directory')
    groups = tree.find("array[@rvXMLIvarName='groups']")

    for group in groups:
        group_out = {
            "color": group.get("color"),
            "hotKey": group[0][0].get("hotKey")
        }
        config_manager["groupConfigs"][group.get("name")] = group_out


def ParseMasterConfigPro7(config_manager):
    print('Parsing "masterConfig_Groups.pro"')
    __file = __file__.decode(sys.getfilesystemencoding())
    dirname = os.path.dirname(os.path.abspath(__file))
    parent_parent_dir = os.path.abspath(os.path.join(os.path.join(dirname, os.pardir), os.pardir))
    presentation = presentation_pb2.Presentation()
    f = open(os.path.join(parent_parent_dir, "config", "masterConfig_Groups.pro"), "rb")
    presentation.ParseFromString(f.read())
    f.close()

    # store all groups in masterconfig
    config_manager["groupConfigs7"] = {}
    for groups in presentation.cue_groups:
        groups.ClearField("cue_identifiers")
        config_manager["groupConfigs7"][groups.group.name] = groups


def ParseConfigFilesPro6(config_manager):
    # loop over all config files in the subfolders
    config_manager["fileConfigs"] = []

    # get the current script directory and search for all config_*.pro6 files in its subdirectories
    __file = __file__.decode(sys.getfilesystemencoding())
    dirname = os.path.dirname(os.path.abspath(__file))

    parent_parent_dir = os.path.abspath(os.path.join(os.path.join(dirname, os.pardir), os.pardir))
    search_regex = parent_parent_dir + "\\config\\config_*.pro6"
    search_result_configs = os.path.join(dirname, search_regex)

    # print ("SEARCH_REGEX: " + search_regex)

    # loop over all config files found in the search
    for config_path in glob.glob(search_result_configs):
        # print which file is being processed
        print('Parsing "{0}"'.format(config_path))
        # create a dictionary to store the extracted data from the current config file
        config_dict = {}
        # save the path of the current config file
        config_dict["path"] = os.path.join(parent_parent_dir, "Output", "Pro6")
        # save the name of the style associated with the current config file
        config_dict["styleName"] = re.search('config_(.*).pro6', config_path).group(1)
        # read config file
        tree = ET.parse(config_path)
        # get needed elements
        rv_presentation_document = tree.getroot()
        groups = rv_presentation_document.find("array[@rvXMLIvarName='groups']")
        group = groups.find("RVSlideGrouping")
        slides = group.find("array[@rvXMLIvarName='slides']")
        slide = slides.find("RVDisplaySlide")

        if "Only one line" == slide.get("notes"):
            config_dict["singleLine"] = True
        else:
            config_dict["singleLine"] = False

        display_elements = slide.find("array[@rvXMLIvarName='displayElements']")
        text_element = display_elements.find(
            "RVTextElement[@displayName='TextElement']")
        rtf_data_text = text_element.find("NSString[@rvXMLIvarName='RTFData']")
        text_style = base64.standard_b64decode(
            rtf_data_text.text).split(b'This is the template Text')[0]
        caption_element = display_elements.find(
            "RVTextElement[@displayName='CaptionTextElement']")
        caption_style = ""
        if caption_element is not None:
            rtf_data_text = caption_element.find(
                "NSString[@rvXMLIvarName='RTFData']")
            caption_style = base64.standard_b64decode(
                rtf_data_text.text).split(b'This is the caption template')[0]
        lower_shape_element = display_elements.find(
            "RVShapeElement[@displayName='BottomLineShapeElement']")
        upper_shape_element = display_elements.find(
            "RVShapeElement[@displayName='TopLineShapeElement']")
        arrangements = rv_presentation_document.find(
            "array[@rvXMLIvarName='arrangements']")
        arrangement = arrangements[0]
        arrangement_ns_string = arrangement[0][0]

        # remove not needed elements
        display_elements.remove(text_element)
        if caption_element is not None:
            display_elements.remove(caption_element)
        if lower_shape_element is not None:
            display_elements.remove(lower_shape_element)
        if upper_shape_element is not None:
            display_elements.remove(upper_shape_element)

        slides.remove(slide)
        groups.remove(group)
        arrangements.remove(arrangement)
        arrangement[0].remove(arrangement_ns_string)
        # add elements to configDict
        config_dict["rvPresentationDocument"] = rv_presentation_document
        config_dict["group"] = group
        config_dict["slide"] = slide
        config_dict["textElement"] = text_element
        config_dict["textStyle"] = text_style
        config_dict["captionElement"] = caption_element
        config_dict["captionStyle"] = caption_style
        config_dict["lowerShapeElement"] = lower_shape_element
        config_dict["upperShapeElement"] = upper_shape_element
        config_dict["arrangement"] = arrangement
        config_dict["arrangementNSString"] = arrangement_ns_string
        # append current config to config list
        config_manager["fileConfigs"].append(config_dict)


def ParseConfigFilesPro7(config_manager):
    # loop over all config files in the subfolders
    config_manager["fileConfigs7"] = []

    __file = __file__.decode(sys.getfilesystemencoding())
    dirname = os.path.dirname(os.path.abspath(__file))

    parent_parent_dir = os.path.abspath(os.path.join(os.path.join(dirname, os.pardir), os.pardir))
    search_regex = parent_parent_dir + "\\config\\config_*.pro"
    search_result_configs = os.path.join(dirname, search_regex)

    for config_path in glob.glob(search_result_configs):
        print('Parsing "{0}"'.format(config_path))
        config_dict = {}

        # save path
        config_dict["path7"] = os.path.join(parent_parent_dir, "Output", "Pro7")

        # save style name
        config_dict["styleName7"] = re.search('config_(.*).pro', config_path).group(1)
        presentation = presentation_pb2.Presentation()
        f = open(config_path, "rb")
        presentation.ParseFromString(f.read())
        f.close()
        presentation.selected_arrangement.Clear()
        presentation.ClearField("cue_groups")
        presentation.ccli.Clear()

        # check if single line and get notesRTF
        if "Only one line" in presentation.cues[0].actions[0].slide.presentation.notes.rtf_data:
            config_dict["singleLine7"] = True
            config_dict["notesRTF7"] = presentation.cues[0].actions[0].slide.presentation.notes.rtf_data.split(
                'Only one line')[0]
        else:
            config_dict["singleLine7"] = False
            config_dict["notesRTF7"] = presentation.cues[0].actions[0].slide.presentation.notes.rtf_data.split(
                'This is the template Text')[0]
            config_dict["notesSecondRTF7"] = presentation.cues[0].actions[0].slide.presentation.notes.rtf_data.split(
                'With second line')[0].split('This is the template Text')[1]
        presentation.cues[0].actions[0].slide.presentation.notes.rtf_data = ""

        # get elements
        for elements in presentation.cues[0].actions[0].slide.presentation.base_slide.elements:
            if elements.element.name == "TextElement":
                config_dict["textElement7"] = elements
                config_dict["textStyle7"] = elements.element.text.rtf_data.split(
                    'This is the template Text')[0]
                if config_dict["singleLine7"] is False:
                    config_dict["textStyleSecond7"] = elements.element.text.rtf_data.split(
                        'With second line')[0].split('This is the template Text')[1]
            elif elements.element.name == "CaptionTextElement":
                config_dict["captionElement7"] = elements
                config_dict["captionStyle7"] = elements.element.text.rtf_data.split(
                    'This is the caption template')[0]
                if config_dict["singleLine7"] is False:
                    config_dict["captionStyleSecond7"] = elements.element.text.rtf_data.split(
                        'and caption second line')[0].split('This is the caption template')[1]
            elif elements.element.name == "BottomLineShapeElement":
                config_dict["lowerShapeElement7"] = elements
            elif elements.element.name == "TopLineShapeElement":
                config_dict["upperShapeElement7"] = elements
        presentation.cues[0].actions[0].slide.presentation.base_slide.ClearField(
            "elements")
        config_dict["slide7"] = presentation.cues[0]
        presentation.ClearField("arrangements")
        presentation.ClearField("cues")
        config_dict["presentation7"] = presentation
        # append current config to config list
        config_manager["fileConfigs7"].append(config_dict)
