class TroubleshootingData:

    RESPONSE_SCHEMA = [
                {
                    "type": "function",
                    "function": {
                        "name": "save_troubleshooting_data",
                        "description": "If a table is given generate an array of problem , possibleCause , proposedSolution triples. IF THERE IS NO TROUBLESHOOTING INFORMATION IN THE GIVEN IMAGE SEND BYPASS AS 'TRUE' . A problem might have multiple causes and a cause might have multiple ways to solutions which can repeat. That's why problem and possible cause can repeat multiple times in the given arrays. Possible array parameters can be like below  ID:['1','2','3','4', '5'], conditionOrProblem: ['boiler is not working','boiler is not working','boiler is not working','boiler never powers on', 'boiler gives error code 400'] , possibleCauseOrThingsToCheck: ['Boiler plug', 'Power indicator', 'Power ON button on the boiler', 'Gas valve', 'Water supply valve'] , proposedSolution: ['Plug the boiler to give electricity', 'If it's given yellow light it means this boiler is not for your electricity type', 'Make sure your power on button is switched to ON', 'Turn gas valve to right to give gas supply', 'Turn water valve to right to give water supply'] ",

                        "parameters": {
                            "type": "object",
                            "properties": {
                                "troubleshooting_objects_array": {
                                    "type": "array",
                                    "description": "Array of objects each object refers to a unique virtual troubleshooting instance",
                                    "items": {
                                        "type": "object",
                                        "properties": {

                                            "conditionOrProblem": {
                                                "type": "string",
                                                "description": "Array of problems you can repeat the same item if same problem has multiple causes and multiple solutions"
                                            },

                                            "possibleCauseOrThingsToCheck": {
                                                "type": "string",
                                                "description": "Possible cause or things to check to solve the problem this field can also repeat"
                                            },
                                            "proposedSolution": {
                                                "type": "string",
                                                "description": "Solution candidate of the given problem and possible cause"
                                            },
                                            "pageNumberShownToHuman": {
                                                "type": "string",
                                                "description": "Page number that exists in the image. Only fill if exists otherwise leave empty by setting ''. Optional. "
                                            },
                                        }
                                    },

                                },
                                "bypass": {
                                    "type": "string",
                                    "description": "Set to 'TRUE' if there is no troubleshooting table in the view. "
                                }
                            },
                            "required": ["troubleshooting_objects_array",
                                         "bypass"],
                        },
                    },
                }
            ]


