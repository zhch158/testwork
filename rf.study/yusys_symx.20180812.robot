*** Settings ***
Documentation     下载公司项目损益明细数据
Library           ./ExtendedSeleniumLibrary.py      timeout=120.0     implicit_wait=0.5        run_on_failure=Capture Page Screenshot
Library           Dialogs
Library           Screenshot
Suite Setup       打开网页      ${登录页}
Suite Teardown    退出

*** Variables ***
${登录页}          http://it.yusys.com.cn/yusys/login.html
${明细页}          http://it.yusys.com.cn/yusys/DeptProfitAndLossDetail/toList.asp
${浏览器}          Chrome
${用户名}          zhengchun
${密码}            Zhch1234
${downloaddir}     C:/Users/郑春/Downloads
# ${downloaddir}     X:/Temp

*** Test Cases ***
登录
    Title Should Start With    资源管理
    Input Text       identifier:loginname   ${用户名}
    Input Text       identifier:password    ${密码}
    ${checkcode}=    Get Value From User    输入验证码        default_value=
    Input Text       identifier:checkcode   ${checkcode}
    Click Button     login_btn
    Wait Until Element Is Enabled   css:#research-system       60

下载损益明细
    [Template]      损益明细
    ${明细页}       完工百分比法    考核口径    2018-06  项目    ${downloaddir}    F:/workspace/python/data


*** Keywords ***
打开网页
    [Arguments]     ${url}
    Open Browser    ${url}          ${浏览器}
    Wait For Condition      return document.readyState=="complete"     60

跳转网页
    [Arguments]     ${url}
    Go to           ${url}
    Wait For Condition      return document.readyState=="complete"     60

选择核算类别
    [Arguments]     ${核算类别}
    Click Element    xpath://div[@id='s2id_accountingmethod']/a/span
    Click Element    css:li.select2-results-dept-0 > div.select2-result-label[title='${核算类别}']

选择报表口径
    [Arguments]     ${报表口径}
    Click Element    css:#s2id_caliber > a.select2-choice > span
    Click Element    css:li.select2-results-dept-0 > div.select2-result-label[title='${报表口径}']

输入查询时间
    [Arguments]     ${查询时间}
    Input Text      identifier:searchtime   ${查询时间}
   
选择项目分类
    [Arguments]     ${项目分类}
    Wait Until Element Is Enabled   css:#s2id_projclassify > a.select2-choice > span       60
    Click Element    css:#s2id_projclassify > a.select2-choice > span
    Click Element    css:li.select2-results-dept-0 > div.select2-result-label[title='${项目分类}']

执行查询
    Click Button     query
    # Wait Until Element Is Enabled     query       120

下载报表结果
    [Arguments]                 ${downloaddir}    ${查询时间}        ${保存目录}
    switch_frame                runqian
    my_wait_until_element_presence   css:img[alt="存为Excel"]       300
    ${原文件}    ${目标文件}=    Get Report Filename     identifier:saveAsName        ${downloaddir}        ${查询时间}        ${保存目录}
    Delete Report File          ${原文件}          ${目标文件}
    Click Element               css:img[alt="存为Excel"]
    Rename File                 ${原文件}          ${目标文件}
    
快照
    Capture Page Screenshot           yusys-{index}.png

退出
    # [Teardown]       Close Browser
    Pause Execution
    Close Browser

损益明细
    [Arguments]     ${报表首页}    ${核算类别}    ${报表口径}    ${查询时间}   ${项目分类}    ${downloaddir}    ${保存目录}
    跳转网页         ${报表首页}      
    选择核算类别     ${核算类别}
    选择报表口径     ${报表口径}
    输入查询时间     ${查询时间}
    选择项目分类     ${项目分类}
    执行查询
    下载报表结果     ${downloaddir}        ${查询时间}        ${保存目录}
