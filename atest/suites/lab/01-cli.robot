*** Settings ***
Documentation       The CLI works.

Library             JupyterLibrary
Resource            ../../resources/Coverage.resource
Resource            ../../resources/Screenshots.resource
Resource            ../../resources/CLI.resource
Resource            ../../resources/LabSelectors.resource
Resource            ../../resources/Commands.resource

Suite Setup         Set Attempt Screenshot Directory    lab${/}cli

Test Tags           suite:cli


*** Variables ***    ***
@{LIST_ARGVS}       list    ls    l
@{RUN_ARGVS}        run    r


*** Test Cases ***
List Commands
    [Documentation]    Commands are listed.
    FOR    ${arg}    IN    @{LIST_ARGVS}
        ${result} =    Run Jyg CLI    ${arg}
        Should Contain    ${result.stdout}    ${CMD_ID_LICENSES}
    END

Run Simple Command
    [Documentation]    A simple command runs.
    FOR    ${arg}    IN    @{RUN_ARGVS}
        Wait Until Page Does Not Contain Element    css:${CSS_LAB_LICENSES}
        ${result} =    Run Jyg CLI    ${arg}    ${CMD_ID_LICENSES}
        Wait Until Page Contains Element    css:${CSS_LAB_LICENSES}
        Should Not Contain    ${result.stdout}    "error"
        Execute JupyterLab Command    Close All Tabs
    END
