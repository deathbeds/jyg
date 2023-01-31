*** Settings ***
Documentation       Variables and keywords for Command Boards


*** Variables ***
${CSS_BOARD_FRAME}      .jp-Jyg-Frame iframe
${CSS_BOARD_SWITCH}     .jp-Jyg-SwitchArea select
@{BOARD_AREA}           left    main    right
&{BOARD_MOD}            left=\#jp-left-stack    right=\#jp-right-stack    main=\#jp-main-dock-panel


*** Keywords ***
Open Board From Launcher
    [Documentation]    Open a command board from the launcher
    [Arguments]    ${title}=All Commands
    ${sel} =    Set Variable    .jp-LauncherCard[title*\="${title} Command Board"]
    Wait Until Element Is Visible    css:${sel}
    Click Element    css:${sel}
    Run Keyword And Ignore Error    Maybe Open JupyterLab Sidebar    ${title}
    Wait Until Element Is Visible    css:${CSS_BOARD_FRAME}

Click Command Element In Board
    [Documentation]    Click an element in a Command Board
    [Arguments]    ${command_id}
    Select Frame    css:${CSS_BOARD_FRAME}
    ${sel} =    Set Variable    [data-command-id\="${command_id}"]
    Wait Until Element Is Visible    css:${sel}
    Click Element    css:${sel}
    [Teardown]    Unselect Frame

Move Board To Area
    [Documentation]    Move a board to another area.
    [Arguments]    ${area}    ${screenshot}
    Select From List By Value    css:${CSS_BOARD_SWITCH}    ${area}
    IF    "${area}" == "popup"
        Wait Until Page Does Not Contain Element    css:${CSS_BOARD_FRAME}
    ELSE
        Wait Until Element Is Visible    css:${BOARD_MOD["${area}"]} ${CSS_BOARD_FRAME}
    END
    Capture Page Screenshot    ${screenshot}
    [Teardown]    Switch Window    MAIN
