*** Settings ***
Documentation     下载公司项目损益明细数据
resource          yusys_resource.robot
Suite Setup       连接网页
# Suite Teardown    退出

*** Variables ***
${Y_M}    2018-06


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
    ${明细页}       完工百分比法    考核口径    ${Y_M}    项目    ${downloaddir}    F:/workspace/python/data/${Y_M}
    ${明细页}       完工百分比法    管理口径    ${Y_M}    项目    ${downloaddir}    F:/workspace/python/data/${Y_M}


*** Keywords ***
损益明细
    [Arguments]     ${报表首页}    ${核算类别}    ${报表口径}    ${查询时间}   ${项目分类}    ${downloaddir}    ${保存目录}
    跳转网页         ${报表首页}      
    选择核算类别     ${核算类别}
    选择报表口径     ${报表口径}
    输入查询时间     ${查询时间}
    选择项目分类     ${项目分类}
    执行查询
    下载报表结果     ${downloaddir}        ${查询时间}        ${保存目录}
