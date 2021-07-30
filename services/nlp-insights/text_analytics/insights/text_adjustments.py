# *******************************************************************************
# IBM Confidential                                                            *
#                                                                             *
# OCO Source Materials                                                        *
#                                                                             *
# (C) Copyright IBM Corp. 2021                                                *
#                                                                             *
# The source code for this program is not published or otherwise              *
# divested of its trade secrets, irrespective of what has been                *
# deposited with the U.S. Copyright Office.                                   *
# ******************************************************************************/


IMMUNIZATION_APPEND = " vaccine"

def adjust_vaccine_text(text):
    # Add "vaccine" to the text so NLP will get codes for the vaccine, not the disease
    # If there is a comma in the text, "vaccine" is added before the comma.  Example:
     #     DTaP, unspecified formulation --> DTaP vaccine, unspecified formulation
    # Otherwise, "vaccine" is added at the end.  Example:
    #     DTaP --> DTaP vaccine
    comma_location = text.find(',')
    if comma_location == -1:
        adjusted_text = text + IMMUNIZATION_APPEND
    else:
        adjusted_text = text[:comma_location] + IMMUNIZATION_APPEND + text[comma_location:len(text)]
    return adjusted_text
