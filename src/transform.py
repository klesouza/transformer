def formatFuncs(config):
    formatter = config['formatter']
    if formatter == "date":
        from datetime import datetime
        import time
        return lambda x: datetime.strptime(x, config["format"]).strftime("%Y-%m-%d %H:%M")
        #return lambda x: {"$date": { "$numberLong": str(int(time.mktime(datetime.strptime(x, config["format"]).timetuple())*1000))}} #datetime.strptime(x, config["format"]).strftime("%Y-%m-%d %H:%M")
    elif formatter == "float":
        return lambda x: float(x) if not "decimal" in config else float(x.replace('.','').replace(config["decimal"], "."))
    elif formatter == "int":
        return lambda x: int(x)
    elif formatter == "mapping":
        return lambda x: config["mapping"][str(x)]
    elif formatter == "static":
        return lambda x: config["value"]
    elif 'padl' in formatter:
        import re
        return lambda x: x.zfill(int(re.search('\((\d+)\)','lpad(11)').group(1)))
    return None
def accessProp(obj, path, value):
    key = path[0]
    if len(path) > 1:
        if key.replace('[]','') not in obj:
            if '[]' in key:
                obj[key.replace('[]','')] = []
                obj[key.replace('[]','')].append({})
            else:
                obj[key] = {}
        if '[]' in key:
            return accessProp(obj[key.replace('[]','')][0], path[1:], value)
        return accessProp(obj[key], path[1:], value)
    obj[key] = value
def transform(line, config):
    obj = {}
    for key,value in config.iteritems():
        try:
            idx = value if isinstance(value, int) else value['source']
            val = line[idx] if isinstance(value, int) or not 'formatter' in value else formatFuncs(value)(line[idx])
            accessProp(obj, key.split('.'), val)
        except:
            print "Erro no mapeamento: ", key
            if "skip_on_error" in value and value["skip_on_error"] == True:
                continue
            raise
    return obj

def transformData(configFile, dataFile, outputFile, limit = None):
    import json, codecs
    config = json.load(open(configFile, 'r'))
    f = codecs.open(dataFile, 'r', encoding = "ISO-8859-1")
    with codecs.open(outputFile, 'w', encoding = "ISO-8859-1") as of:
        of.write('[')
    line = f.readline()
    idx = 0
    for k,c in config.iteritems():
        if not isinstance(c,int) and 'id' in c:
            idx = k
    id = None
    i = 0
    lasttransformed = None
    first = True
    for line in f:
        if limit and i > limit:
            break
        try:
            transformed = transform(line.replace('\r\n', '').split(';'), config)
        except:
            print "Erro no registro: ", i
            raise
        if id == transformed[idx]:
            for c,v in transformed.iteritems():
                if isinstance(v, list):
                    for l in v:
                        if l not in lasttransformed[c]:
                            lasttransformed[c].append(l)
        else:
            if lasttransformed != None:
                with codecs.open(outputFile, 'a', encoding = "ISO-8859-1") as of:
                    of.write((',' if not first else '') +json.dumps(lasttransformed))
                first = False
            lasttransformed = transformed
            i += 1
        id = transformed[idx]
    with codecs.open(outputFile, 'a', encoding = "ISO-8859-1") as of:
        if lasttransformed != None:
            of.write((',' if not first else '') +json.dumps(lasttransformed))
        of.write(']')
    print 'registros: ', i

if __name__ == '__main__':
    import sys, time
    print 'Processando...'
    start_time = time.time()
    transformData(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else None)
    print("--- %s seconds ---" % (time.time() - start_time))
#transformData('C:\\Users\\kleber.silva\\Desktop\\SAFe\\backtest cativa\\mapper.json', 'C:\\Users\\kleber.silva\\Desktop\\SAFe\\backtest cativa\\pedidos.csv')
