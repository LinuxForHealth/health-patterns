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
 
# from text_analytics.call_acd_then_enhance import call_acd_with_text_then_enhance
from text_analytics.call_nlp_then_enhance import call_service_then_enhance

# from text_analytics.config import config

test_string = "Took care of breast cancer by using celecoxib"

result = call_service_then_enhance(test_string)
print("Result of calling ACD: " , result)
