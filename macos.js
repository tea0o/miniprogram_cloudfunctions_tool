var NSData = ObjC.classes.NSData;
var NSString = ObjC.classes.NSString;
function str(s) {
    return Memory.allocUtf8String(s);
}
function nsstr(str) {
    return ObjC.classes.NSString.stringWithUTF8String_(Memory.allocUtf8String(str));
}
/* NSString -> NSData */
function nsstr2nsdata(nsstr) {
    return nsstr.dataUsingEncoding_(4);
}
/* NSData -> NSString */
function nsdata2nsstr(nsdata) {
    return ObjC.classes.NSString.alloc().initWithData_encoding_(nsdata, 4);
}
console.log("-----------------mac微信小程序注入完成-----------");
try{
    Interceptor.attach(ObjC.classes.WAJSEventHandler_operateWXData['- requestDataWithAppID:data:'].implementation,{
      onEnter: function(args) {
        var d = new ObjC.Object(args[3]);
        var s = nsdata2nsstr(d);
        console.log("请求包:"+s.toString());
        send({type: 'REQ', data: s.toString()})
        var op = recv('NEW_REQ', function(val) {
          var s = val.payload;
          var ns = ObjC.classes.NSString.stringWithString_(s);
          var new_s= nsstr2nsdata(ns);
          args[3] = new_s;
        });
        op.wait()
    
      },
      onLeave: function(retval) {
  
      }

  });
  Interceptor.attach(ObjC.classes.WAJSEventHandler_operateWXData['- endWithResult:'].implementation,{
      onEnter: function(args) {
        const dict = new ObjC.Object(args[2]);
        var respond_data=dict.objectForKey_('data').objectForKey_('data');
        send({type: 'RESP', data: respond_data.toString()});
        console.log("-------------------------------------");
        console.log("返回包:"+ respond_data.toString());
        var op = recv('NEW_RESP', function(val) {
          var new_data = val.payload;
          var repond_data = ObjC.classes.NSMutableDictionary.alloc().init();
          var repond_data_1 =ObjC.classes.NSMutableDictionary.alloc().init();
          const enumerator = dict.keyEnumerator();
          let key;
          const enumerator1 = dict.objectForKey_('data').keyEnumerator();
          while ((key = enumerator1.nextObject()) !== null) {
              if(key =="data"){
                repond_data_1.setObject_forKey_(nsstr(new_data),key);
              }else{
                repond_data_1.setObject_forKey_(dict.objectForKey_('data').objectForKey_(key),key);
              }
          }
          while ((key = enumerator.nextObject()) !== null) {
              if(key =="data"){
                repond_data.setObject_forKey_(repond_data_1,key);
              }else{
                repond_data.setObject_forKey_(dict.objectForKey_(key),key);
              }
          }
          args[2]=repond_data;
        });
        op.wait();
      },
      onLeave: function(retval) {
      }

  });
}
catch(err){
    console.log("[!] Exception2: " + err.message);
}