*** Settings ***
Documentation       The Boards work.

Library             JupyterLibrary
Resource            ../../resources/Coverage.resource
Resource            ../../resources/Screenshots.resource
Resource            ../../resources/Boards.resource
Resource            ../../resources/LabSelectors.resource
Resource            ../../resources/Commands.resource

Suite Setup         Set Attempt Screenshot Directory    lab${/}boards
Test Setup          Execute JupyterLab Command    Close All Tabs
Test Teardown       Clean Up Board Test

Test Tags           suite:boards


*** Test Cases ***
Open Board
    [Documentation]    Commands in a board work.
    Open Board From Launcher
    Capture Page Screenshot    00-opened.png
    Click Command Element In Board    ${CMD_ID_LICENSES}
    Wait Until Element Is Visible    css:${CSS_LAB_LICENSES}
    Capture Page Screenshot    00-executed.png

Boards Can Move
    [Documentation]    Can move boards.
    Open Board From Launcher
    Capture Page Screenshot    00-opened.png
    FOR    ${i}    ${area}    IN ENUMERATE    @{BOARD_AREA}
        Move Board To Area    ${area}    01-moved-${i}-${area}.png
    END
    Move Board To Area    popup    02-removed-popup.png


*** Keywords ***
Clean Up Board Test
    [Documentation]    Clean up after a test
    Switch Window    MAIN
    Execute JupyterLab Command    Close All Tabs
    Execute JupyterLab Command    Close All Command Boards
