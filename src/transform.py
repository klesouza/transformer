class Transformer:
    options = {
        'config_file': "mapper.json",
        'data_file': "data.csv",
        'output_file': "outpout.json",
        'encoding': "ISO-8859-1",
        'sep': ";",
        'limit': None,
        'header': True,
        'verbose': True
    }
    def __init__(self, custom_options = {}):
        self.options.update(custom_options)

    def _formatFuncs(self, config):
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
    def _accessProp(self, obj, path, value):
        key = path[0]
        if len(path) > 1:
            if key.replace('[]','') not in obj:
                if '[]' in key:
                    obj[key.replace('[]','')] = []
                    obj[key.replace('[]','')].append({})
                else:
                    obj[key] = {}
            if '[]' in key:
                return self._accessProp(obj[key.replace('[]','')][0], path[1:], value)
            return self._accessProp(obj[key], path[1:], value)
        obj[key] = value

    def _transform(self, line, config):
        obj = {}
        for key,value in config.iteritems():
            try:
                idx = value if isinstance(value, int) else value['source']
                val = line[idx] if isinstance(value, int) or not 'formatter' in value else self._formatFuncs(value)(line[idx])
                self._accessProp(obj, key.split('.'), val)
            except:
                print "Erro no mapeamento: ", key
                if "skip_on_error" in value and value["skip_on_error"] == True:
                    continue
                raise
        return obj

    def _log(self, str):
        if self.options["verbose"]:
            print str
    def do(self):
        import json, codecs
        config = json.load(open(self.options["config_file"], 'r'))
        f = codecs.open(self.options["data_file"], 'r', encoding = self.options["encoding"])
        with codecs.open(self.options["output_file"], 'w', encoding = self.options["encoding"]) as of:
            of.write('[')
        if self.options["header"]:
            line = f.readline()
        idx = 0
        for k,c in config.iteritems():
            if not isinstance(c,int) and 'id' in c:
                idx = k
        id = None
        i = 0
        lasttransformed = None
        first = True
        limit = self.options["limit"]
        for line in f:
            if limit and i >= limit:
                break
            try:
                transformed = self._transform(line.replace('\r\n', '').split(self.options["sep"]), config)
            except:
                self._log("Erro no registro: {}".format(i))
                raise
            if id == transformed[idx]:
                for c,v in transformed.iteritems():
                    if isinstance(v, list):
                        for l in v:
                            if l not in lasttransformed[c]:
                                lasttransformed[c].append(l)
            else:
                if lasttransformed != None:
                    with codecs.open(self.options["output_file"], 'a', encoding = self.options["encoding"]) as of:
                        of.write((',' if not first else '') +json.dumps(lasttransformed))
                    first = False
                lasttransformed = transformed
                i += 1
            id = transformed[idx]
        with codecs.open(self.options["output_file"], 'a', encoding = self.options["encoding"]) as of:
            if lasttransformed != None:
                of.write((',' if not first else '') +json.dumps(lasttransformed))
            of.write(']')
        self._log('registros: {}'.format(i))
if __name__ == '__main__':
    import sys, time
    print 'Processando...'
    start_time = time.time()
    t = Transformer({'config_file': sys.argv[1], 'data_file': sys.argv[2],'output_file': sys.argv[3], 'limit': int(sys.argv[4]) if len(sys.argv) > 4 else None})
    t.do()
    print("--- %s seconds ---" % (time.time() - start_time))
