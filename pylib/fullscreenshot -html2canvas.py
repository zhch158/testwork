from selenium import webdriver
from selenium.webdriver.common.by import By 
import time
import io
import os,sys
import base64
import exescript

def getFileContent(filePath):
    f=open(filePath, "r", encoding="utf-8")
    fileContent=f.read()
    f.close()
    return fileContent

def scroll_page(browser, jsHandle, step_ms=100):
    jsstr="""
    (function () {{
        var y = 0;
        var step = 100;
        var step_ms={0};
        window.scroll(0, 0);

        function f() {{
            if (y < document.body.scrollHeight) {{
                y += step;
                window.scroll(0, y);
                setTimeout(f, step_ms);
            }} else {{
                window.scroll(0, 0);
                document.title += "scroll-done";
            }}
        }}

        setTimeout(f, 1000);
    }})()""".format

    jsHandle.exeWrap(jsstr(step_ms))
    for i in range(30):
        if "scroll-done" in browser.title:
            break
        else:
            time.sleep(10)
    return 0

def take_screenshot_by_html2canvas(browser, jsHandle, filename="capture.png"):
    element=browser.find_element_by_tag_name("body")
    s_height=element.get_attribute("scrollHeight")
    s_width=element.get_attribute("scrollWidth")
    size=element.size
    print("scrollHeight[%s] scrollWidth[%s], size[%s]" %(s_height, s_width, size))

    scroll_page(browser, jsHandle, 200)

    jsHandle.loadJs("https://html2canvas.hertzen.com/dist/html2canvas.js")
    # time.sleep(20) #waiting for loadjs finished
    # jsStr="var __selenium_result__; html2canvas(document.body, {async:false, useCORS:true}).then(function(canvas) {var img = canvas.toDataURL('image/png').replace('data:image/png;base64,', ''); __selenium_result__=img; return __selenium_result__; }); return __selenium_result__"
    jsStr="""(function(){
        html2canvas(document.body, {async:false, useCORS:true}).then(function(canvas){
            var img = canvas.toDataURL('image/png').replace('data:image/png;base64,', ''); 
            var el=document.getElementById("__s_msg");
            el.setAttribute("msg",img);}); 
    })()""" 
    i=0
    load_flag=False
    while(i<=10 and load_flag==False):
        i+=1
        try:
            jsHandle.exeWrap(jsStr)
        except Exception as e:
            if("html2canvas is not defined" in str(e)):
                print("waiting for html2canvas loaded[%d]" %i)
                time.sleep(10)
                load_flag=False
                continue
            else:
                raise
        load_flag=True
    if(i>10 or load_flag==False):
        raise ValueError('html2canvas not found[%s]' %jsStr)

    result=None
    i=0
    while(i<=10):
        i+=1
        result=jsHandle.getMsg()
        if(result==None or result=="undefined"):
            print("waiting for screenshot result[%d]" %i)
            time.sleep(10)
        else:
            break
    if(i>10):
        raise ValueError("get screenshot" %browser.title)

    # jsFile = getFileContent("./html2canvas.js")
    # jsFile += " var webDriverCallback = arguments[arguments.length - 1]; html2canvas(document.body, {onrendered: function(canvas) {var img = canvas.toDataURL('image/png').replace('data:image/png;base64,', '');; webDriverCallback(img); }"
    # result=browser.execute_script(jsStr)

    imageString = str(result)
    imageData= base64.b64decode(imageString)
    outfile=open(filename,"wb")
    outfile.write(imageData)
    outfile.close()

if __name__ == "__main__":
    if(len(sys.argv)==1):
        sys.argv+=["http://it.yusys.com.cn/yusys/login.html"]
    url=sys.argv[1]
    browser = webdriver.Firefox() # Get local session of firefox
    # browser.set_window_size(1200, 900)
    browser.maximize_window()
    browser.implicitly_wait(60)
    browser.get(url) # Load page

    exejs=exescript.ExeJs(browser)
    take_screenshot_by_html2canvas(browser, exejs)
    # take_screenshot("http://codingpy.com")
    # take_screenshot("http://news.sina.com.cn")
    # take_screenshot_by_html2canvas("http://news.sina.com.cn")

    browser.quit()
