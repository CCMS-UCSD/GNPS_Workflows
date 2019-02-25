
function spsConn()
{
  var xmlhttp;

  try { 
    this.xmlhttp = new ActiveXObject("Msxml2.XMLHTTP"); 
  } catch (e) { 
    try { 
      this.xmlhttp = new ActiveXObject("Microsoft.XMLHTTP"); 
    } catch (e) { 
      try { 
        this.xmlhttp = new XMLHttpRequest(); 
      } catch (e) { 
        this.xmlhttp = false; 
      }
    }
  }

  if (!this.xmlhttp) return null;


  this.connect = function(sURL, sMethod, sVars, fnWhenDone)
  {
    if (!this.xmlhttp) return false;
    
    sMethod = sMethod.toUpperCase();

    try {
      if (sMethod == "GET") {
        this.xmlhttp.open(sMethod, sURL+"?"+sVars, true);
        sVars = null;
      } else {
        this.xmlhttp.open(sMethod, sURL, true);
        this.xmlhttp.setRequestHeader("Method", "POST "+sURL+" HTTP/1.1");
        this.xmlhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
      }
      
      this.xmlhttp.onreadystatechange = function() 
      {
        if (this.readyState == 4) {
          if(this.status == 200) {
            fnWhenDone(this);
          } else { 
            alert('\n\nThere was a problem with the request.\n\nStatus code: '+this.status+'\n'+this.statusText); 
          }
        }
      };

      this.xmlhttp.send(sVars);

    } catch(z) { 
      return false;
    }
    return true;
  };
  
  return this;
}

