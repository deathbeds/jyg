*** Settings ***
Documentation       The Boards work.

Library             JupyterLibrary
Resource            ../../resources/Coverage.resource
Resource            ../../resources/Screenshots.resource
Resource            ../../resources/Boards.resource
Resource            ../../resources/LabSelectors.resource
Resource            ../../resources/Commands.resource

Suite Setup         Set Attempt Screenshot Directory    lab${/}boards

Test Tags           suite:boards


*** Test Cases ***
Open Board
    [Documentation]    Commands in a board work.
    Open Board From Launcher
    Capture Page Screenshot    00-opened.png
    Select Frame    css:${CSS_BOARD_FRAME}
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
