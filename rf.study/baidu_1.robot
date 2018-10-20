*** Settings ***
Documentation     Simple example using SeleniumLibrary.
Library           SeleniumLibrary     timeout=5.0     implicit_wait=2.0        run_on_failure=Capture Page Screenshot
Library           Dialogs
Library           Screenshot
Suite Setup       打开网页      ${首页}        ${网页标题}
Suite Teardown    退出

*** Variables ***
${首页}          https://www.baidu.com/
${浏览器}        Chrome
${搜素关键字}    姜夔暗香
${网页标题}      百度一下

*** Test Cases ***
查看百度百科
    # Register Keyword To Run On Failure         Capture Page Screenshot
    # Set Selenium Implicit Wait                 30
    # 打开网页        ${首页}     ${网页标题}
    ${search}=     输入搜索内容      ${搜素关键字}
    搜索
    内容匹配        ${search}
    进入百科       \_百度百科
    Pause Execution
    快照
    # 退出

*** Keywords ***
打开网页
    [Arguments]     ${url}          ${title_start}
    Open Browser    ${url}          ${浏览器}
    ${title}=       Get Title
    Should Start With      ${title}    ${title_start}

输入搜索内容
    [Arguments]    ${words}
    ${words}=      Get Value From User       搜索内容        default_value=${words}
    Input Text     identifier:kw   ${words}
    [Return]       ${words}

搜索
    Click Button    su

内容匹配
    [Arguments]      ${words}
    Wait For Condition    return document.title == "${words}\_百度搜索"        timeout=10
    ${title}=       Get Title
    Should Start With      ${title}    ${words}
    # Page Should Contain   ${搜素关键字} 

进入百科
    [Arguments]      ${words}
    Click Element    partial link:${words}
    Select Window    NEW
    ${title}=       Get Title
    Should End With      ${title}    ${words}

快照
    Capture Page Screenshot           baidu-{index}.png

退出
    # [Teardown]       Close Browser
    Close Browser