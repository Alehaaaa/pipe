def loadCSS(pathCSS):
    try:
        with open(pathCSS, "r") as myfile:
            cssContent = myfile.read().replace('\n', '')
            return cssContent
    except:
        return ''
