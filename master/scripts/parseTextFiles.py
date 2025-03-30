#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
import io
import unicodedata
import json


# Global configuration
print_style = "CONSOLE"


def PrintC(style, content):
    """Print content based on the specified style."""
    if style == "CONSOLE":
        print(content)
    else:
        print(content + "<br>")


def ParseSlide(input, position, output, startingLine):
    """Parse a single slide from the input and add it to the output.
    
    Args:
        input: List of lines from the input file
        position: Current position in the input
        output: List to append the slide to
        startingLine: Line number for error reporting
        
    Returns:
        New position after parsing the slide
    """
    slide = []
    # slide has at least one line so it can be added directly
    slide.append(input[position].strip())
    lines = 1
    
    # if slide has two lines add second line
    if position + lines < len(input) and input[position + lines] != "":
        slide.append(input[position + lines].strip())
        lines += 1
        
    # check for empty line after slide
    if position + lines < len(input) and input[position + lines] != "":
        raise ValueError("EmptyLineError | line: {0} | An empty line was expected after the end of the slide.".format(
            startingLine + lines))
            
    output.append(slide)
    return position + lines + 1


def ParseGroup(input, position, output, groupConfig, startingLine):
    """Parse a group of slides from the input and add it to the output.
    
    Args:
        input: List of lines from the input file
        position: Current position in the input
        output: Dictionary to add the group to
        groupConfig: Configuration of valid group names
        startingLine: Line number for error reporting
        
    Returns:
        New position after parsing the group
    """
    # check if group name is as required
    if input[position] not in groupConfig:
        raise ValueError("UnknownGroupError | line: {0} | The group '{1}' was not found.".format(
            startingLine, input[position]))
    elif input[position] in output:
        raise ValueError("GroupUsedTwice | line: {0} | The group '{1}' was used multiple times.".format(
            position + 1, input[position]))
    else:
        name = input[position]
        output[name] = []
        
        # check empty line after group name
        if input[position + 1] != "":
            raise ValueError("EmptyLineError | line: {0} | An empty line was expected after group '{1}' but not found.".format(
                startingLine + 1, output["name"]))
        else:
            i = position + 2
            # loop over all slides until next group is found
            while i < len(input):
                if input[i] in groupConfig:
                    break
                i = ParseSlide(input, i, output[name], startingLine + i - position)
                
    return i


def ParseLanguage(input, groupConfig, startingLine):
    """Parse a language section from the input.
    
    Args:
        input: String containing the language section
        groupConfig: Configuration of valid group names
        startingLine: Line number for error reporting
        
    Returns:
        Dictionary containing the parsed language data
    """
    language = {}
    input = input.split("\n")
    language["name"] = input[0]
    language["groups"] = {}

    idx = 1

    if input[1].startswith("CCLI="):
        idx = 2

    # check for empty line after language name
    if input[idx] != "":
        raise ValueError("EmptyLineError | line: {0} | An empty line was expected after language '{1}' but not found.".format(
            startingLine + idx, language["name"]))
            
    i = idx + 1
    # loop over all input data and parse groups
    while i < len(input):
        i = ParseGroup(input, i, language["groups"], groupConfig, startingLine + i)
        
    return language


def ParseCCLI(input, lang):
    """Parse the CCLI number from the input.
    
    Args:
        input: String containing the language section
        lang: Language name
        
    Returns:
        CCLI number as string or None if not found
    """
    # check if first line starts with CCLI=
    first_line = input.split("\n")[1]
    if first_line.startswith("CCLI="):
        ccli_number = first_line.split("=")[1]
    else:
        ccli_number = None

    PrintC(print_style, u'{0}_{1}'.format(lang, ccli_number))

    return ccli_number


def ParseArrangement(input, position, output, groupConfig, startingLine):
    """Parse an arrangement from the input and add it to the output.
    
    Args:
        input: List of lines from the input file
        position: Current position in the input
        output: List to append the arrangement to
        groupConfig: Configuration of valid group names
        startingLine: Line number for error reporting
        
    Returns:
        New position after parsing the arrangement
    """
    arrangement = {}
    arrangement["name"] = input[position]
    
    # check for empty line after arrangement name
    if input[position + 1] != "":
        raise ValueError("EmptyLineError", "line: {0} | An empty line was expected after arrangement '{1}' but not found.".format(
            startingLine + 1, arrangement["name"]))
    else:
        i = position + 2
        arrangement["order"] = []
        
        # loop over all groups in arrangement, verify they are as required and add them to the arrangement
        while i < len(input) and input[i] != "":
            if input[i] not in groupConfig:
                raise ValueError("UnknownGroupError | line: {0} | The group '{1}' was not found in the masterConfig.".format(
                    startingLine + i - position, input[i]))
            else:
                arrangement["order"].append(input[i])
            i += 1
            
        output.append(arrangement)
        
    return i + 1


def ParseArrangements(input, groupConfig, startingLine):
    """Parse the arrangements section from the input.
    
    Args:
        input: String containing the arrangements section
        groupConfig: Configuration of valid group names
        startingLine: Line number for error reporting
        
    Returns:
        List of parsed arrangements
    """
    splitInput = input.split("\n")
    arrangements = []
    
    if splitInput[0] != "Arrangements":
        raise ValueError(
            "KeyWordError | line: {0} | The KeyWord 'Arrangements' was expected but not found.".format(startingLine))
    elif len(splitInput) == 1:
        # no arrangement available
        pass
    elif splitInput[1] != "":
        raise ValueError(
            "EmptyLineError | line: {0} | An empty line was expected after KeyWord 'Arrangements' but not found.".format(startingLine + 1))
    else:
        idx = 1
        if splitInput[1].startswith("CCLI="):
            idx = 2

        i = idx + 1
        while i < len(splitInput):
            i = ParseArrangement(splitInput, i, arrangements, groupConfig, startingLine + i)
            
    return arrangements


def CheckOutput(output):
    """Verify the parsed output for consistency between languages.
    
    Args:
        output: Dictionary containing the parsed data
        
    Raises:
        ValueError: If inconsistencies are found between languages
    """
    # if two languages check all groups have same number of slides and lines per slide
    if len(output["languages"]) == 2:
        # check if both languages have same number of groups
        if len(output["languages"][0]["groups"]) != len(output["languages"][1]["groups"]):
            raise ValueError("GroupError | - | The language '{0}' has '{1}' groups but language '{2}' has '{3}'".format(
                output["languages"][0]["name"],
                len(output["languages"][0]["groups"]),
                output["languages"][1]["name"],
                len(output["languages"][1]["groups"])
            ))
            
        # check if all groups are in both languages
        for group in output["languages"][0]["groups"]:
            if group not in output["languages"][1]["groups"]:
                raise ValueError("GroupError | group: {0} | The group '{1}' was found in language '{2}' but not in '{3}'".format(
                    group, group, 
                    output["languages"][0]["name"],
                    output["languages"][1]["name"]
                ))
                
        # check if all groups have same number of slides and lines per slide
        for group in output["languages"][0]["groups"]:
            if len(output["languages"][0]["groups"][group]) != len(output["languages"][1]["groups"][group]):
                raise ValueError("GroupError | group: {0} | The group '{1}' has '{2}' slides in language '{3}' but '{4}' slides in language '{5}'".format(
                    group, group,
                    len(output["languages"][0]["groups"][group]),
                    output["languages"][0]["name"],
                    len(output["languages"][1]["groups"][group]),
                    output["languages"][1]["name"]
                ))
                
            for i in range(0, len(output["languages"][0]["groups"][group])):
                if len(output["languages"][0]["groups"][group][i]) != len(output["languages"][1]["groups"][group][i]):
                    raise ValueError("SlideError | group: {0} | Slide number '{1}' in group '{2}' has '{3}' lines in language '{4}' but '{5}' lines in language '{6}'".format(
                        group, i, group,
                        len(output["languages"][0]["groups"][group][i]),
                        output["languages"][0]["name"],
                        len(output["languages"][1]["groups"][group][i]),
                        output["languages"][1]["name"]
                    ))
                    
        # check if arrangements only consist of available groups
        for arrangement in output["arrangements"]:
            for group in arrangement["order"]:
                if group not in output["languages"][0]["groups"] and group != "Instrumental":
                    raise ValueError("ArrangementError | arrangement: {0} | The group '{1}' used in arrangement '{2}' was not found".format(
                        arrangement["name"], group, arrangement["name"]
                    ))


def ParseTextFile(directory, file, groupConfig):
    """Parse a text file containing song lyrics in one or two languages and arrangements.
    
    Args:
        directory: Directory containing the file
        file: Filename to parse
        groupConfig: Configuration of valid group names
        
    Returns:
        Dictionary containing the parsed data
    """
    # read input file
    f = codecs.open(os.path.join(directory, file).encode('utf-8'), encoding='utf-8') 
    originalInput = f.read()
    f.close()
    
    output = {}
    output["name"] = unicodedata.normalize("NFC", file).replace(".txt", "")
    output["languages"] = []
    output["CCLI_number"] = {}

    # remove trailing newlines
    originalInput = originalInput.replace("\r", "").rstrip("\n")
    
    # split file into segments. One for each language and one for the arrangements
    input = originalInput.split("\n\n\n")
    
    # parse first language
    lang1 = ParseLanguage(input[0], groupConfig, 1)
    PrintC(print_style, u'lang1 {0}'.format(json.dumps(lang1, indent=2)))

    output["CCLI_number"][lang1["name"]] = ParseCCLI(input[0], lang1["name"])    
    output["languages"].append(lang1)
    
    # parse second language if available
    if len(input) == 3:
        pos = originalInput.find(input[1])
        line = originalInput.count("\n", 0, pos) + 1
        lang2 = ParseLanguage(input[1], groupConfig, line)

        PrintC(print_style, u'lang2 {0}'.format(json.dumps(lang2, indent=2)))

        output["CCLI_number"][lang2["name"]] = ParseCCLI(input[1], lang2["name"])
        output["languages"].append(lang2)
        
    # parse arrangements
    pos = originalInput.find(input[-1])
    line = originalInput.count("\n", 0, pos) + 1

    PrintC(print_style, u'arrangements {0}'.format(input[-1]))
    output["arrangements"] = ParseArrangements(input[-1], groupConfig, line)

    CheckOutput(output)

    return output
