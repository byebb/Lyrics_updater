# -- coding: utf-8 --

import uuid
from pp7_pb2 import basicTypes_pb2, presentation_pb2
import os
import copy


# We need a function that converts UTF-8 codes of vowel mutations in the German language correctly.
# Otherwise, we have a lot of gibberish in PP7 output files...
def ReplaceSpecialCharacters(text):
    output = copy.deepcopy(text)
    for i in range(0, len(output)):
        # Ä
        #text[i] = text[i].replace(chr(195) + chr(8222), "\\'c4")
        #text[i] = text[i].replace("Ä", "\\'c4")
        output[i] = output[i].replace(u'\u00c4', "\\'c4")
        # Ö
        #text[i] = text[i].replace(chr(195) + chr(8211), "\\'d6")
        #text[i] = text[i].replace("Ö", "\\'d6")
        output[i] = output[i].replace(u'\u00d6', "\\'d6")
        # Ü
        #text[i] = text[i].replace(chr(195) + chr(339), "\\'dc")
        #text[i] = text[i].replace("Ü", "\\'dc")
        output[i] = output[i].replace(u'\u00dc', "\\'dc")
        # ä
        #text[i] = text[i].replace(chr(195) + chr(164), "\\'e4")
        #text[i] = text[i].replace("ä", "\\'e4")
        output[i] = output[i].replace(u'\u00e4', "\\'e4")
        # ö
        #text[i] = text[i].replace(chr(195) + chr(182), "\\'f6")
        #text[i] = text[i].replace("ö", "\\'f6")
        output[i] = output[i].replace(u'\u00f6', "\\'f6")
        # ü
        #text[i] = text[i].replace(chr(195) + chr(188), "\\'fc")
        #text[i] = text[i].replace("ü", "\\'fc")
        output[i] = output[i].replace(u'\u00fc', "\\'fc")
        # ß
        #text[i] = text[i].replace(chr(195) + chr(376), "\\'df")
        #text[i] = text[i].replace("ß", "\\'df")
        output[i] = output[i].replace(u'\u00df', "ss")
        # ’
        #text[i] = text[i].replace(chr(226) + chr(8364) + chr(8482), "\\'27")
        #text[i] = text[i].replace("’", "\\'27")
        output[i] = output[i].replace(u'\u2019', "\\'27")
        output[i] = output[i].encode()
    return output


def ReplaceSpecialCharactersUPPER(text):
    output = copy.deepcopy(text)
    for i in range(0, len(output)):
        output[i] = output[i].replace(u'\u00e4', "\\'c4")        # ä -> Ä
        output[i] = output[i].replace(u'\u00c4', "\\'c4")        # Ä -> Ä
        output[i] = output[i].replace(u'\u00f6', "\\'d6")        # ö -> Ö
        output[i] = output[i].replace(u'\u00d6', "\\'d6")        # Ö -> Ö
        output[i] = output[i].replace(u'\u00fc', "\\'dc")        # ü -> Ü
        output[i] = output[i].replace(u'\u00dc', "\\'dc")        # Ü -> Ü
        output[i] = output[i].replace(u'\u2019', "\\'27")        # ’

        # ß --> ss/SS doesn matter, since we apply .upper() anyway, only not working for utf8 codes
        output[i] = output[i].replace(u'\u00df', "SS")

        output[i] = output[i].encode()
    return output


def CreateSlide(config, presentation, text, caption):

    debug_output = False

    slide = copy.deepcopy(config["slide7"])

    # update uuid
    slide_uuid = [str(uuid.uuid4())]
    slide.uuid.string = slide_uuid[0]
    slide.actions[0].uuid.string = str(uuid.uuid4())
    slide.actions[0].slide.presentation.base_slide.uuid.string = str(uuid.uuid4())

    my_text = ReplaceSpecialCharacters(text)

    # IN CASE WE NEED IT UPPERCASE
    my_text = ReplaceSpecialCharactersUPPER(text)

    # create notes
    notes = config["notesRTF7"] + my_text[0]
    if (config["singleLine7"] == False) and (len(my_text) == 2):
        notes += config["notesSecondRTF7"] + my_text[1]
    notes += "}"
    slide.actions[0].slide.presentation.notes.rtf_data = notes

    # add text element
    if debug_output:
        print(my_text[0])
        print("[LYR1] " + my_text[0].upper())

    text_element = copy.deepcopy(config["textElement7"])
    text_element.element.uuid.string = str(uuid.uuid4())
    rft_text = config["textStyle7"] + my_text[0].upper()

    if config["singleLine7"] is False and len(my_text) == 2:
        rft_text += config["textStyleSecond7"] + my_text[1].upper()
        if debug_output:
            print("[LYR2] " + my_text[1].upper())

    rft_text += "}"
    text_element.element.text.rtf_data = rft_text
    slide.actions[0].slide.presentation.base_slide.elements.append(text_element)

    # add caption element
    if "captionElement7" in config and caption is not None:
        my_caption = ReplaceSpecialCharacters(caption)

        if debug_output:
            print ("[CAPT] " + ", ".join(my_caption))

        caption_element = copy.deepcopy(config["captionElement7"])
        caption_element.element.uuid.string = str(uuid.uuid4())
        rft_caption = config["captionStyle7"] + my_caption[0]
        if (config["singleLine7"] == False) and (len(my_caption) == 2):
            rft_caption += config["captionStyleSecond7"] + my_caption[1]
        rft_caption += "}"
        caption_element.element.text.rtf_data = rft_caption
        slide.actions[0].slide.presentation.base_slide.elements.append(
            caption_element)

    # add lower shape element
    if "lowerShapeElement7" in config:
        lower_shape = copy.deepcopy(config["lowerShapeElement7"])
        lower_shape.element.uuid.string = str(uuid.uuid4())
        slide.actions[0].slide.presentation.base_slide.elements.append(
            lower_shape)

    # add upper shape element
    if ("upperShapeElement7" in config) and (False == config["singleLine7"]) and (len(text) == 2):
        upper_shape = copy.deepcopy(config["upperShapeElement7"])
        upper_shape.element.uuid.string = str(uuid.uuid4())
        slide.actions[0].slide.presentation.base_slide.elements.append(
            upper_shape)
    presentation.cues.append(slide)

    # create second slide in case single line is true
    if (True == config["singleLine7"]) and (len(text) == 2):
        slide = copy.deepcopy(config["slide7"])
        # update uuid
        slide_uuid.append(str(uuid.uuid4()))
        slide.uuid.string = slide_uuid[1]
        slide.actions[0].uuid.string = str(uuid.uuid4())
        slide.actions[0].slide.presentation.base_slide.uuid.string = str(
            uuid.uuid4())
        # create notes
        notes = config["notesRTF7"] + my_text[1] + "}"
        slide.actions[0].slide.presentation.notes.rtf_data = notes
        # add text element
        text_element = copy.deepcopy(config["textElement7"])
        text_element.element.uuid.string = str(uuid.uuid4())
        rft_text = config["textStyle7"] + my_text[1].upper() + "}"
        text_element.element.text.rtf_data = rft_text
        slide.actions[0].slide.presentation.base_slide.elements.append(
            text_element)
        # add caption element
        if "captionElement7" in config and caption is not None:
            my_caption = ReplaceSpecialCharacters(caption)
            caption_element = copy.deepcopy(config["captionElement7"])
            caption_element.element.uuid.string = str(uuid.uuid4())
            rft_caption = config["captionStyle7"] + my_caption[1] + "}"
            caption_element.element.text.rtf_data = rft_caption
            slide.actions[0].slide.presentation.base_slide.elements.append(
                caption_element)
        # add lower shape element
        if "lowerShapeElement7" in config:
            lower_shape = copy.deepcopy(config["lowerShapeElement7"])
            lower_shape.element.uuid.string = str(uuid.uuid4())
            slide.actions[0].slide.presentation.base_slide.elements.append(
                lower_shape)
        presentation.cues.append(slide)
    return slide_uuid


def CreateGroup(config, group_config, presentation, name, language, caption):
    group = copy.deepcopy(group_config[name])

    # update uuid
    group_uuid = str(uuid.uuid4())
    group.group.uuid.string = group_uuid

    # create slides
    for i in range(0, len(language)):
        if caption is None:
            caption_text = None
        else:
            caption_text = caption[i]
        slide_uuid_str = CreateSlide(
            config, presentation, language[i], caption_text)

        # add slides to group
        for slide in slide_uuid_str:
            slide_uuid = basicTypes_pb2.UUID()
            slide_uuid.string = slide
            group.cue_identifiers.append(slide_uuid)
    presentation.cue_groups.append(group)
    return group_uuid


def CreateInstrumental(config, group_config, presentation):
    # add Instrumental group
    group = copy.deepcopy(group_config[group_config.keys()[0]])

    # update uuid
    group_uuid = str(uuid.uuid4())
    group.group.uuid.string = group_uuid
    group.group.name = "Instrumental"
    group.group.color.Clear()
    group.group.hotKey.Clear()

    # add Instrumental slide
    slide = copy.deepcopy(config["slide7"])

    # update uuid
    slide_uuid_str = str(uuid.uuid4())
    slide.uuid.string = slide_uuid_str
    slide.actions[0].uuid.string = str(uuid.uuid4())
    slide.actions[0].slide.presentation.base_slide.uuid.string = str(uuid.uuid4())
    presentation.cues.append(slide)
    slide_uuid = basicTypes_pb2.UUID()
    slide_uuid.string = slide_uuid_str
    group.cue_identifiers.append(slide_uuid)
    presentation.cue_groups.append(group)
    return group_uuid


def CreateArrangements(config, presentation, arrangements, uuids):
    for arrangement in arrangements:
        arr = presentation_pb2.Presentation.Arrangement()
        arrUuid = str(uuid.uuid4())
        arr.uuid.string = arrUuid
        arr.name = arrangement["name"]
        for group in arrangement["order"]:
            uuidGroup = basicTypes_pb2.UUID()
            uuidGroup.string = uuids[group]
            arr.group_identifiers.append(uuidGroup)
        presentation.arrangements.append(arr)
        presentation.selected_arrangement.string = arrUuid


def CreateOutput(config, groupConfig, name, language, caption, arrangements):
    presentation = copy.deepcopy(config["presentation7"])
    #update uuid
    presentation.uuid.string = str(uuid.uuid4())
    #update name
    songName = "{0}_{1}_{2}".format(
        name.encode('ascii','ignore'), language["name"], config["styleName7"])
    presentation.name = songName
    uuids = {}
    # create groups
    for group in language["groups"]:
        if caption == None:
            captionGroup = None
        else:
            captionGroup = caption["groups"][group]
        uuids[group] = CreateGroup(config, groupConfig, presentation, group,
                                   language["groups"][group], captionGroup)
    # create Instrumental
    uuids["Instrumental"] = CreateInstrumental(
        config, groupConfig, presentation)
    # create arrangements
    CreateArrangements(config, presentation, arrangements, uuids)
    # write output to file
    file = os.path.join(
        config["path7"], u"{0}_{1}_{2}.pro".format(name, language["name"],
                                                   config["styleName7"]))
    f = open(file, 'wb')
    f.write(presentation.SerializeToString())
    f.close()


def CreateOutputs(config, groupConfig, inputText):
    # check if two languages are provided
    if len(inputText["languages"]) == 2:
        CreateOutput(config, groupConfig, inputText["name"],
                     inputText["languages"][0], inputText["languages"][1],
                     inputText["arrangements"])
        CreateOutput(config, groupConfig, inputText["name"],
                     inputText["languages"][1], inputText["languages"][0],
                     inputText["arrangements"])
    else:
        CreateOutput(config, groupConfig, inputText["name"],
                     inputText["languages"][0], None,
                     inputText["arrangements"])
