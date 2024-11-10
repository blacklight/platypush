(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[7594],{6590:function(e){(function(t,n){e.exports=n()})(globalThis,(()=>(()=>{"use strict";var e={794:(e,t,n)=>{Object.defineProperty(t,"__esModule",{value:!0}),t.CronParser=void 0;var i=n(586),r=function(){function e(e,t,n){void 0===t&&(t=!0),void 0===n&&(n=!1),this.expression=e,this.dayOfWeekStartIndexZero=t,this.monthStartIndexZero=n}return e.prototype.parse=function(){var e,t,n=null!==(e=this.expression)&&void 0!==e?e:"";if(n.startsWith("@")){var i=this.parseSpecial(this.expression);t=this.extractParts(i)}else t=this.extractParts(this.expression);return this.normalize(t),this.validate(t),t},e.prototype.parseSpecial=function(e){var t={"@yearly":"0 0 1 1 *","@annually":"0 0 1 1 *","@monthly":"0 0 1 * *","@weekly":"0 0 * * 0","@daily":"0 0 * * *","@midnight":"0 0 * * *","@hourly":"0 * * * *"},n=t[e];if(!n)throw new Error("Unknown special expression.");return n},e.prototype.extractParts=function(e){if(!this.expression)throw new Error("cron expression is empty");for(var t=e.trim().split(/[ ]+/),n=0;n<t.length;n++)if(t[n].includes(",")){var i=t[n].split(",").map((function(e){return e.trim()})).filter((function(e){return""!==e})).map((function(e){return isNaN(Number(e))?e:Number(e)})).filter((function(e){return null!==e&&""!==e}));0===i.length&&i.push("*"),i.sort((function(e,t){return null!==e&&null!==t?e-t:0})),t[n]=i.map((function(e){return null!==e?e.toString():""})).join(",")}if(t.length<5)throw new Error("Expression has only ".concat(t.length," part").concat(1==t.length?"":"s",". At least 5 parts are required."));if(5==t.length)t.unshift(""),t.push("");else if(6==t.length){var r=/\d{4}$/.test(t[5])||"?"==t[4]||"?"==t[2];r?t.unshift(""):t.push("")}else if(t.length>7)throw new Error("Expression has ".concat(t.length," parts; too many!"));return t},e.prototype.normalize=function(e){var t=this;if(e[3]=e[3].replace("?","*"),e[5]=e[5].replace("?","*"),e[2]=e[2].replace("?","*"),0==e[0].indexOf("0/")&&(e[0]=e[0].replace("0/","*/")),0==e[1].indexOf("0/")&&(e[1]=e[1].replace("0/","*/")),0==e[2].indexOf("0/")&&(e[2]=e[2].replace("0/","*/")),0==e[3].indexOf("1/")&&(e[3]=e[3].replace("1/","*/")),0==e[4].indexOf("1/")&&(e[4]=e[4].replace("1/","*/")),0==e[6].indexOf("1/")&&(e[6]=e[6].replace("1/","*/")),e[5]=e[5].replace(/(^\d)|([^#/\s]\d)/g,(function(e){var n=e.replace(/\D/,""),i=n;return t.dayOfWeekStartIndexZero?"7"==n&&(i="0"):i=(parseInt(n)-1).toString(),e.replace(n,i)})),"L"==e[5]&&(e[5]="6"),"?"==e[3]&&(e[3]="*"),e[3].indexOf("W")>-1&&(e[3].indexOf(",")>-1||e[3].indexOf("-")>-1))throw new Error("The 'W' character can be specified only when the day-of-month is a single day, not a range or list of days.");var n={SUN:0,MON:1,TUE:2,WED:3,THU:4,FRI:5,SAT:6};for(var i in n)e[5]=e[5].replace(new RegExp(i,"gi"),n[i].toString());e[4]=e[4].replace(/(^\d{1,2})|([^#/\s]\d{1,2})/g,(function(e){var n=e.replace(/\D/,""),i=n;return t.monthStartIndexZero&&(i=(parseInt(n)+1).toString()),e.replace(n,i)}));var r={JAN:1,FEB:2,MAR:3,APR:4,MAY:5,JUN:6,JUL:7,AUG:8,SEP:9,OCT:10,NOV:11,DEC:12};for(var o in r)e[4]=e[4].replace(new RegExp(o,"gi"),r[o].toString());"0"==e[0]&&(e[0]=""),/\*|\-|\,|\//.test(e[2])||!/\*|\//.test(e[1])&&!/\*|\//.test(e[0])||(e[2]+="-".concat(e[2]));for(var a=0;a<e.length;a++)if(-1!=e[a].indexOf(",")&&(e[a]=e[a].split(",").filter((function(e){return""!==e})).join(",")||"*"),"*/1"==e[a]&&(e[a]="*"),e[a].indexOf("/")>-1&&!/^\*|\-|\,/.test(e[a])){var s=null;switch(a){case 4:s="12";break;case 5:s="6";break;case 6:s="9999";break;default:s=null;break}if(null!==s){var l=e[a].split("/");e[a]="".concat(l[0],"-").concat(s,"/").concat(l[1])}}},e.prototype.validate=function(e){this.assertNoInvalidCharacters("DOW",e[5]),this.assertNoInvalidCharacters("DOM",e[3]),this.validateRange(e)},e.prototype.validateRange=function(e){i.default.secondRange(e[0]),i.default.minuteRange(e[1]),i.default.hourRange(e[2]),i.default.dayOfMonthRange(e[3]),i.default.monthRange(e[4],this.monthStartIndexZero),i.default.dayOfWeekRange(e[5],this.dayOfWeekStartIndexZero)},e.prototype.assertNoInvalidCharacters=function(e,t){var n=t.match(/[A-KM-VX-Z]+/gi);if(n&&n.length)throw new Error("".concat(e," part contains invalid values: '").concat(n.toString(),"'"))},e}();t.CronParser=r},728:(e,t,n)=>{Object.defineProperty(t,"__esModule",{value:!0}),t.ExpressionDescriptor=void 0;var i=n(910),r=n(794),o=function(){function e(t,n){if(this.expression=t,this.options=n,this.expressionParts=new Array(5),!this.options.locale&&e.defaultLocale&&(this.options.locale=e.defaultLocale),!e.locales[this.options.locale]){var i=Object.keys(e.locales)[0];console.warn("Locale '".concat(this.options.locale,"' could not be found; falling back to '").concat(i,"'.")),this.options.locale=i}this.i18n=e.locales[this.options.locale],void 0===n.use24HourTimeFormat&&(n.use24HourTimeFormat=this.i18n.use24HourTimeFormatByDefault())}return e.toString=function(t,n){var i=void 0===n?{}:n,r=i.throwExceptionOnParseError,o=void 0===r||r,a=i.verbose,s=void 0!==a&&a,l=i.dayOfWeekStartIndexZero,u=void 0===l||l,c=i.monthStartIndexZero,p=void 0!==c&&c,h=i.use24HourTimeFormat,d=i.locale,f=void 0===d?null:d,m=i.tzOffset,v=void 0===m?0:m,y={throwExceptionOnParseError:o,verbose:s,dayOfWeekStartIndexZero:u,monthStartIndexZero:p,use24HourTimeFormat:h,locale:f,tzOffset:v},g=new e(t,y);return g.getFullDescription()},e.initialize=function(t,n){void 0===n&&(n="en"),e.specialCharacters=["/","-",",","*"],e.defaultLocale=n,t.load(e.locales)},e.prototype.getFullDescription=function(){var e="";try{var t=new r.CronParser(this.expression,this.options.dayOfWeekStartIndexZero,this.options.monthStartIndexZero);this.expressionParts=t.parse();var n=this.getTimeOfDayDescription(),i=this.getDayOfMonthDescription(),o=this.getMonthDescription(),a=this.getDayOfWeekDescription(),s=this.getYearDescription();e+=n+i+a+o+s,e=this.transformVerbosity(e,!!this.options.verbose),e=e.charAt(0).toLocaleUpperCase()+e.substr(1)}catch(l){if(this.options.throwExceptionOnParseError)throw"".concat(l);e=this.i18n.anErrorOccuredWhenGeneratingTheExpressionD()}return e},e.prototype.getTimeOfDayDescription=function(){var t=this.expressionParts[0],n=this.expressionParts[1],r=this.expressionParts[2],o="";if(i.StringUtilities.containsAny(n,e.specialCharacters)||i.StringUtilities.containsAny(r,e.specialCharacters)||i.StringUtilities.containsAny(t,e.specialCharacters))if(t||!(n.indexOf("-")>-1)||n.indexOf(",")>-1||n.indexOf("/")>-1||i.StringUtilities.containsAny(r,e.specialCharacters))if(!t&&r.indexOf(",")>-1&&-1==r.indexOf("-")&&-1==r.indexOf("/")&&!i.StringUtilities.containsAny(n,e.specialCharacters)){var a=r.split(",");o+=this.i18n.at();for(var s=0;s<a.length;s++)o+=" ",o+=this.formatTime(a[s],n,""),s<a.length-2&&(o+=","),s==a.length-2&&(o+=this.i18n.spaceAnd())}else{var l=this.getSecondsDescription(),u=this.getMinutesDescription(),c=this.getHoursDescription();if(o+=l,o&&u&&(o+=", "),o+=u,u===c)return o;o&&c&&(o+=", "),o+=c}else{var p=n.split("-");o+=i.StringUtilities.format(this.i18n.everyMinuteBetweenX0AndX1(),this.formatTime(r,p[0],""),this.formatTime(r,p[1],""))}else o+=this.i18n.atSpace()+this.formatTime(r,n,t);return o},e.prototype.getSecondsDescription=function(){var e=this,t=this.getSegmentDescription(this.expressionParts[0],this.i18n.everySecond(),(function(e){return e}),(function(t){return i.StringUtilities.format(e.i18n.everyX0Seconds(t),t)}),(function(t){return e.i18n.secondsX0ThroughX1PastTheMinute()}),(function(t){return"0"==t?"":parseInt(t)<20?e.i18n.atX0SecondsPastTheMinute(t):e.i18n.atX0SecondsPastTheMinuteGt20()||e.i18n.atX0SecondsPastTheMinute(t)}));return t},e.prototype.getMinutesDescription=function(){var e=this,t=this.expressionParts[0],n=this.expressionParts[2],r=this.getSegmentDescription(this.expressionParts[1],this.i18n.everyMinute(),(function(e){return e}),(function(t){return i.StringUtilities.format(e.i18n.everyX0Minutes(t),t)}),(function(t){return e.i18n.minutesX0ThroughX1PastTheHour()}),(function(i){try{return"0"==i&&-1==n.indexOf("/")&&""==t?e.i18n.everyHour():parseInt(i)<20?e.i18n.atX0MinutesPastTheHour(i):e.i18n.atX0MinutesPastTheHourGt20()||e.i18n.atX0MinutesPastTheHour(i)}catch(r){return e.i18n.atX0MinutesPastTheHour(i)}}));return r},e.prototype.getHoursDescription=function(){var e=this,t=this.expressionParts[2],n=this.getSegmentDescription(t,this.i18n.everyHour(),(function(t){return e.formatTime(t,"0","")}),(function(t){return i.StringUtilities.format(e.i18n.everyX0Hours(t),t)}),(function(t){return e.i18n.betweenX0AndX1()}),(function(t){return e.i18n.atX0()}));if(n&&t.includes("-")&&"0"!=this.expressionParts[1]){var r=Array.from(n.matchAll(/:00/g));if(r.length>1){var o=r[r.length-1].index;n=n.substring(0,o)+":59"+n.substring(o+3)}}return n},e.prototype.getDayOfWeekDescription=function(){var e=this,t=this.i18n.daysOfTheWeek(),n=null;return n="*"==this.expressionParts[5]?"":this.getSegmentDescription(this.expressionParts[5],this.i18n.commaEveryDay(),(function(n,i){var r=n;n.indexOf("#")>-1?r=n.substring(0,n.indexOf("#")):n.indexOf("L")>-1&&(r=r.replace("L",""));var o=parseInt(r);if(e.options.tzOffset){var a=e.expressionParts[2],s=parseInt(a)+(e.options.tzOffset?e.options.tzOffset:0);s>=24?o++:s<0&&o--,o>6?o=0:o<0&&(o=6)}var l=e.i18n.daysOfTheWeekInCase?e.i18n.daysOfTheWeekInCase(i)[o]:t[o];if(n.indexOf("#")>-1){var u=null,c=n.substring(n.indexOf("#")+1),p=n.substring(0,n.indexOf("#"));switch(c){case"1":u=e.i18n.first(p);break;case"2":u=e.i18n.second(p);break;case"3":u=e.i18n.third(p);break;case"4":u=e.i18n.fourth(p);break;case"5":u=e.i18n.fifth(p);break}l=u+" "+l}return l}),(function(t){return 1==parseInt(t)?"":i.StringUtilities.format(e.i18n.commaEveryX0DaysOfTheWeek(t),t)}),(function(t){var n=t.substring(0,t.indexOf("-")),i="*"!=e.expressionParts[3];return i?e.i18n.commaAndX0ThroughX1(n):e.i18n.commaX0ThroughX1(n)}),(function(t){var n=null;if(t.indexOf("#")>-1){var i=t.substring(t.indexOf("#")+1);n=e.i18n.commaOnThe(i).trim()+e.i18n.spaceX0OfTheMonth()}else if(t.indexOf("L")>-1)n=e.i18n.commaOnTheLastX0OfTheMonth(t.replace("L",""));else{var r="*"!=e.expressionParts[3];n=r?e.i18n.commaAndOnX0():e.i18n.commaOnlyOnX0(t)}return n})),n},e.prototype.getMonthDescription=function(){var e=this,t=this.i18n.monthsOfTheYear(),n=this.getSegmentDescription(this.expressionParts[4],"",(function(n,i){return i&&e.i18n.monthsOfTheYearInCase?e.i18n.monthsOfTheYearInCase(i)[parseInt(n)-1]:t[parseInt(n)-1]}),(function(t){return 1==parseInt(t)?"":i.StringUtilities.format(e.i18n.commaEveryX0Months(t),t)}),(function(t){return e.i18n.commaMonthX0ThroughMonthX1()||e.i18n.commaX0ThroughX1()}),(function(t){return e.i18n.commaOnlyInMonthX0?e.i18n.commaOnlyInMonthX0():e.i18n.commaOnlyInX0()}));return n},e.prototype.getDayOfMonthDescription=function(){var e=this,t=null,n=this.expressionParts[3];switch(n){case"L":t=this.i18n.commaOnTheLastDayOfTheMonth();break;case"WL":case"LW":t=this.i18n.commaOnTheLastWeekdayOfTheMonth();break;default:var r=n.match(/(\d{1,2}W)|(W\d{1,2})/);if(r){var o=parseInt(r[0].replace("W","")),a=1==o?this.i18n.firstWeekday():i.StringUtilities.format(this.i18n.weekdayNearestDayX0(),o.toString());t=i.StringUtilities.format(this.i18n.commaOnTheX0OfTheMonth(),a);break}var s=n.match(/L-(\d{1,2})/);if(s){var l=s[1];t=i.StringUtilities.format(this.i18n.commaDaysBeforeTheLastDayOfTheMonth(l),l);break}if("*"==n&&"*"!=this.expressionParts[5])return"";t=this.getSegmentDescription(n,this.i18n.commaEveryDay(),(function(t){return"L"==t?e.i18n.lastDay():e.i18n.dayX0?i.StringUtilities.format(e.i18n.dayX0(),t):t}),(function(t){return"1"==t?e.i18n.commaEveryDay():e.i18n.commaEveryX0Days(t)}),(function(t){return e.i18n.commaBetweenDayX0AndX1OfTheMonth(t)}),(function(t){return e.i18n.commaOnDayX0OfTheMonth(t)}));break}return t},e.prototype.getYearDescription=function(){var e=this,t=this.getSegmentDescription(this.expressionParts[6],"",(function(e){return/^\d+$/.test(e)?new Date(parseInt(e),1).getFullYear().toString():e}),(function(t){return i.StringUtilities.format(e.i18n.commaEveryX0Years(t),t)}),(function(t){return e.i18n.commaYearX0ThroughYearX1()||e.i18n.commaX0ThroughX1()}),(function(t){return e.i18n.commaOnlyInYearX0?e.i18n.commaOnlyInYearX0():e.i18n.commaOnlyInX0()}));return t},e.prototype.getSegmentDescription=function(e,t,n,r,o,a){var s=null,l=e.indexOf("/")>-1,u=e.indexOf("-")>-1,c=e.indexOf(",")>-1;if(e)if("*"===e)s=t;else if(l||u||c)if(c){for(var p=e.split(","),h="",d=0;d<p.length;d++)if(d>0&&p.length>2&&(h+=",",d<p.length-1&&(h+=" ")),d>0&&p.length>1&&(d==p.length-1||2==p.length)&&(h+="".concat(this.i18n.spaceAnd()," ")),p[d].indexOf("/")>-1||p[d].indexOf("-")>-1){var f=p[d].indexOf("-")>-1&&-1==p[d].indexOf("/"),m=this.getSegmentDescription(p[d],t,n,r,f?this.i18n.commaX0ThroughX1:o,a);f&&(m=m.replace(", ","")),h+=m}else h+=l?this.getSegmentDescription(p[d],t,n,r,o,a):n(p[d]);s=l?h:i.StringUtilities.format(a(e),h)}else if(l){p=e.split("/");if(s=i.StringUtilities.format(r(p[1]),p[1]),p[0].indexOf("-")>-1){var v=this.generateRangeSegmentDescription(p[0],o,n);0!=v.indexOf(", ")&&(s+=", "),s+=v}else if(-1==p[0].indexOf("*")){var y=i.StringUtilities.format(a(p[0]),n(p[0]));y=y.replace(", ",""),s+=i.StringUtilities.format(this.i18n.commaStartingX0(),y)}}else u&&(s=this.generateRangeSegmentDescription(e,o,n));else s=i.StringUtilities.format(a(e),n(e));else s="";return s},e.prototype.generateRangeSegmentDescription=function(e,t,n){var r="",o=e.split("-"),a=n(o[0],1),s=n(o[1],2),l=t(e);return r+=i.StringUtilities.format(l,a,s),r},e.prototype.formatTime=function(e,t,n){var i=0,r=0;this.options.tzOffset&&(i=this.options.tzOffset>0?Math.floor(this.options.tzOffset):Math.ceil(this.options.tzOffset),r=parseFloat((this.options.tzOffset%1).toFixed(2)),0!=r&&(r*=60));var o=parseInt(e)+i,a=parseInt(t)+r;a>=60?(a-=60,o+=1):a<0&&(a+=60,o-=1),o>=24?o-=24:o<0&&(o=24+o);var s="",l=!1;this.options.use24HourTimeFormat||(l=!(!this.i18n.setPeriodBeforeTime||!this.i18n.setPeriodBeforeTime()),s=l?"".concat(this.getPeriod(o)," "):" ".concat(this.getPeriod(o)),o>12&&(o-=12),0===o&&(o=12));var u="";return n&&(u=":".concat(("00"+n).substring(n.length))),"".concat(l?s:"").concat(("00"+o.toString()).substring(o.toString().length),":").concat(("00"+a.toString()).substring(a.toString().length)).concat(u).concat(l?"":s)},e.prototype.transformVerbosity=function(e,t){return t||(e=e.replace(new RegExp(", ".concat(this.i18n.everyMinute()),"g"),""),e=e.replace(new RegExp(", ".concat(this.i18n.everyHour()),"g"),""),e=e.replace(new RegExp(this.i18n.commaEveryDay(),"g"),""),e=e.replace(/\, ?$/,"")),e},e.prototype.getPeriod=function(e){return e>=12?this.i18n.pm&&this.i18n.pm()||"PM":this.i18n.am&&this.i18n.am()||"AM"},e.locales={},e}();t.ExpressionDescriptor=o},336:(e,t,n)=>{Object.defineProperty(t,"__esModule",{value:!0}),t.enLocaleLoader=void 0;var i=n(751),r=function(){function e(){}return e.prototype.load=function(e){e["en"]=new i.en},e}();t.enLocaleLoader=r},751:(e,t)=>{Object.defineProperty(t,"__esModule",{value:!0}),t.en=void 0;var n=function(){function e(){}return e.prototype.atX0SecondsPastTheMinuteGt20=function(){return null},e.prototype.atX0MinutesPastTheHourGt20=function(){return null},e.prototype.commaMonthX0ThroughMonthX1=function(){return null},e.prototype.commaYearX0ThroughYearX1=function(){return null},e.prototype.use24HourTimeFormatByDefault=function(){return!1},e.prototype.anErrorOccuredWhenGeneratingTheExpressionD=function(){return"An error occured when generating the expression description.  Check the cron expression syntax."},e.prototype.everyMinute=function(){return"every minute"},e.prototype.everyHour=function(){return"every hour"},e.prototype.atSpace=function(){return"At "},e.prototype.everyMinuteBetweenX0AndX1=function(){return"Every minute between %s and %s"},e.prototype.at=function(){return"At"},e.prototype.spaceAnd=function(){return" and"},e.prototype.everySecond=function(){return"every second"},e.prototype.everyX0Seconds=function(){return"every %s seconds"},e.prototype.secondsX0ThroughX1PastTheMinute=function(){return"seconds %s through %s past the minute"},e.prototype.atX0SecondsPastTheMinute=function(){return"at %s seconds past the minute"},e.prototype.everyX0Minutes=function(){return"every %s minutes"},e.prototype.minutesX0ThroughX1PastTheHour=function(){return"minutes %s through %s past the hour"},e.prototype.atX0MinutesPastTheHour=function(){return"at %s minutes past the hour"},e.prototype.everyX0Hours=function(){return"every %s hours"},e.prototype.betweenX0AndX1=function(){return"between %s and %s"},e.prototype.atX0=function(){return"at %s"},e.prototype.commaEveryDay=function(){return", every day"},e.prototype.commaEveryX0DaysOfTheWeek=function(){return", every %s days of the week"},e.prototype.commaX0ThroughX1=function(){return", %s through %s"},e.prototype.commaAndX0ThroughX1=function(){return", %s through %s"},e.prototype.first=function(){return"first"},e.prototype.second=function(){return"second"},e.prototype.third=function(){return"third"},e.prototype.fourth=function(){return"fourth"},e.prototype.fifth=function(){return"fifth"},e.prototype.commaOnThe=function(){return", on the "},e.prototype.spaceX0OfTheMonth=function(){return" %s of the month"},e.prototype.lastDay=function(){return"the last day"},e.prototype.commaOnTheLastX0OfTheMonth=function(){return", on the last %s of the month"},e.prototype.commaOnlyOnX0=function(){return", only on %s"},e.prototype.commaAndOnX0=function(){return", and on %s"},e.prototype.commaEveryX0Months=function(){return", every %s months"},e.prototype.commaOnlyInX0=function(){return", only in %s"},e.prototype.commaOnTheLastDayOfTheMonth=function(){return", on the last day of the month"},e.prototype.commaOnTheLastWeekdayOfTheMonth=function(){return", on the last weekday of the month"},e.prototype.commaDaysBeforeTheLastDayOfTheMonth=function(){return", %s days before the last day of the month"},e.prototype.firstWeekday=function(){return"first weekday"},e.prototype.weekdayNearestDayX0=function(){return"weekday nearest day %s"},e.prototype.commaOnTheX0OfTheMonth=function(){return", on the %s of the month"},e.prototype.commaEveryX0Days=function(){return", every %s days"},e.prototype.commaBetweenDayX0AndX1OfTheMonth=function(){return", between day %s and %s of the month"},e.prototype.commaOnDayX0OfTheMonth=function(){return", on day %s of the month"},e.prototype.commaEveryHour=function(){return", every hour"},e.prototype.commaEveryX0Years=function(){return", every %s years"},e.prototype.commaStartingX0=function(){return", starting %s"},e.prototype.daysOfTheWeek=function(){return["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]},e.prototype.monthsOfTheYear=function(){return["January","February","March","April","May","June","July","August","September","October","November","December"]},e}();t.en=n},586:(e,t)=>{function n(e,t){if(!e)throw new Error(t)}Object.defineProperty(t,"__esModule",{value:!0});var i=function(){function e(){}return e.secondRange=function(e){for(var t=e.split(","),i=0;i<t.length;i++)if(!isNaN(parseInt(t[i],10))){var r=parseInt(t[i],10);n(r>=0&&r<=59,"seconds part must be >= 0 and <= 59")}},e.minuteRange=function(e){for(var t=e.split(","),i=0;i<t.length;i++)if(!isNaN(parseInt(t[i],10))){var r=parseInt(t[i],10);n(r>=0&&r<=59,"minutes part must be >= 0 and <= 59")}},e.hourRange=function(e){for(var t=e.split(","),i=0;i<t.length;i++)if(!isNaN(parseInt(t[i],10))){var r=parseInt(t[i],10);n(r>=0&&r<=23,"hours part must be >= 0 and <= 23")}},e.dayOfMonthRange=function(e){for(var t=e.split(","),i=0;i<t.length;i++)if(!isNaN(parseInt(t[i],10))){var r=parseInt(t[i],10);n(r>=1&&r<=31,"DOM part must be >= 1 and <= 31")}},e.monthRange=function(e,t){for(var i=e.split(","),r=0;r<i.length;r++)if(!isNaN(parseInt(i[r],10))){var o=parseInt(i[r],10);n(o>=1&&o<=12,t?"month part must be >= 0 and <= 11":"month part must be >= 1 and <= 12")}},e.dayOfWeekRange=function(e,t){for(var i=e.split(","),r=0;r<i.length;r++)if(!isNaN(parseInt(i[r],10))){var o=parseInt(i[r],10);n(o>=0&&o<=6,t?"DOW part must be >= 0 and <= 6":"DOW part must be >= 1 and <= 7")}},e}();t["default"]=i},910:(e,t)=>{Object.defineProperty(t,"__esModule",{value:!0}),t.StringUtilities=void 0;var n=function(){function e(){}return e.format=function(e){for(var t=[],n=1;n<arguments.length;n++)t[n-1]=arguments[n];return e.replace(/%s/g,(function(e){for(var n=[],i=1;i<arguments.length;i++)n[i-1]=arguments[i];return t.shift()}))},e.containsAny=function(e,t){return t.some((function(t){return e.indexOf(t)>-1}))},e}();t.StringUtilities=n}},t={};function n(i){var r=t[i];if(void 0!==r)return r.exports;var o=t[i]={exports:{}};return e[i](o,o.exports,n),o.exports}var i={};return(()=>{var e=i;Object.defineProperty(e,"__esModule",{value:!0}),e.toString=void 0;var t=n(728),r=n(336);t.ExpressionDescriptor.initialize(new r.enLocaleLoader),e["default"]=t.ExpressionDescriptor;var o=t.ExpressionDescriptor.toString;e.toString=o})(),i})()))},1808:function(e,t,n){"use strict";n.d(t,{A:function(){return v}});var i=n(641),r=n(33),o=n(3751);const a={class:"slider-wrapper"},s=["textContent"],l=["textContent"],u={class:"slider-container"},c=["min","max","step","disabled","value"],p=["textContent"];function h(e,t,n,h,d,f){return(0,i.uX)(),(0,i.CE)("label",a,[n.withRange?((0,i.uX)(),(0,i.CE)("span",{key:0,class:(0,r.C4)(["range-labels",{"with-label":n.withLabel}])},[n.withRange?((0,i.uX)(),(0,i.CE)("span",{key:0,class:"label left",textContent:(0,r.v_)(n.range[0])},null,8,s)):(0,i.Q3)("",!0),n.withRange?((0,i.uX)(),(0,i.CE)("span",{key:1,class:"label right",textContent:(0,r.v_)(n.range[1])},null,8,l)):(0,i.Q3)("",!0)],2)):(0,i.Q3)("",!0),(0,i.Lk)("span",u,[(0,i.Lk)("input",{class:(0,r.C4)(["slider",{"with-label":n.withLabel}]),type:"range",min:n.range[0],max:n.range[1],step:n.step,disabled:n.disabled,value:n.value,ref:"range",onInput:t[0]||(t[0]=(0,o.D$)((t=>e.$emit("input",t)),["stop"])),onChange:t[1]||(t[1]=(0,o.D$)((t=>e.$emit("change",t)),["stop"]))},null,42,c),n.withLabel?((0,i.uX)(),(0,i.CE)("span",{key:0,class:"label",textContent:(0,r.v_)(n.value),ref:"label"},null,8,p)):(0,i.Q3)("",!0)])])}var d={emits:["input","change"],props:{value:{type:Number},disabled:{type:Boolean,default:!1},range:{type:Array,default:()=>[0,100]},step:{type:Number,default:1},withLabel:{type:Boolean,default:!1},withRange:{type:Boolean,default:!1}}},f=n(6262);const m=(0,f.A)(d,[["render",h],["__scopeId","data-v-d90e850c"]]);var v=m},11:function(e,t,n){"use strict";n.d(t,{A:function(){return f}});var i=n(641),r=n(33),o=n(3751);const a=e=>((0,i.Qi)("data-v-eff375b6"),e=e(),(0,i.jt)(),e),s=["checked","id"],l=a((()=>(0,i.Lk)("div",{class:"switch"},[(0,i.Lk)("div",{class:"dot"})],-1))),u={class:"label"};function c(e,t,n,a,c,p){return(0,i.uX)(),(0,i.CE)("div",{class:(0,r.C4)(["power-switch",{disabled:n.disabled}]),onClick:t[0]||(t[0]=(0,o.D$)(((...e)=>p.onInput&&p.onInput(...e)),["stop"]))},[(0,i.Lk)("input",{type:"checkbox",checked:n.value,id:n.id},null,8,s),(0,i.Lk)("label",null,[l,(0,i.Lk)("span",u,[(0,i.RG)(e.$slots,"default",{},void 0,!0)])])],2)}var p={name:"ToggleSwitch",emits:["input"],props:{id:{type:String},value:{type:Boolean,default:!1},disabled:{type:Boolean,default:!1}},methods:{onInput(e){if(this.disabled)return!1;this.$emit("input",e)}}},h=n(6262);const d=(0,h.A)(p,[["render",c],["__scopeId","data-v-eff375b6"]]);var f=d},7594:function(e,t,n){"use strict";n.r(t),n.d(t,{default:function(){return Ue}});var i=n(641),r=n(33),o=n(3751);const a=e=>((0,i.Qi)("data-v-5f15d80f"),e=e(),(0,i.jt)(),e),s={class:"head"},l={class:"row item"},u={class:"col-8"},c={key:0,class:"col-4 buttons"},p=a((()=>(0,i.Lk)("i",{class:"fas fa-undo"},null,-1))),h=[p],d=a((()=>(0,i.Lk)("button",{type:"submit",class:"save-btn",title:"Save"},[(0,i.Lk)("i",{class:"fas fa-save"})],-1))),f={class:"body"},m={class:"row item"},v={class:"name"},y=a((()=>(0,i.Lk)("label",null,[(0,i.Lk)("i",{class:"icon fas fa-question"}),(0,i.eW)(" Condition ")],-1))),g=a((()=>(0,i.Lk)("br",null,null,-1))),k=a((()=>(0,i.Lk)("span",{class:"subtext"},[(0,i.Lk)("span",{class:"text"},[(0,i.eW)(" The condition that must be met for the alarm to trigger. "),(0,i.Lk)("a",{href:"https://crontab.guru",target:"_blank"},"Cron syntax"),(0,i.eW)(" is supported. ")])],-1))),b={class:"condition-type radio"},x={class:"value"},L=["value"],O={class:"row item"},S=a((()=>(0,i.Lk)("div",{class:"name"},[(0,i.Lk)("label",null,[(0,i.Lk)("i",{class:"icon fas fa-music"}),(0,i.eW)(" Media ")]),(0,i.Lk)("br"),(0,i.Lk)("span",{class:"subtext"},[(0,i.Lk)("span",{class:"text"}," Path or URL of the media resource to play when the alarm triggers. ")])],-1))),X={class:"value file-selector"},w={class:"row item"},T=a((()=>(0,i.Lk)("div",{class:"name"},[(0,i.Lk)("label",null,[(0,i.Lk)("i",{class:"icon fas fa-puzzle-piece"}),(0,i.eW)(" Media Plugin ")]),(0,i.Lk)("br"),(0,i.Lk)("span",{class:"subtext"},[(0,i.Lk)("span",{class:"text"}," The plugin to use to play the media resource. ")])],-1))),D={class:"value"},I={class:"row item"},C=a((()=>(0,i.Lk)("div",{class:"name"},[(0,i.Lk)("label",null,[(0,i.Lk)("i",{class:"icon fas fa-repeat"}),(0,i.eW)(" Repeat Media ")]),(0,i.Lk)("br"),(0,i.Lk)("span",{class:"subtext"},[(0,i.Lk)("span",{class:"text"}," Whether to repeat the media resource when it finishes playing if the alarm is still running. ")])],-1))),E={class:"value"},M={class:"row item"},F=a((()=>(0,i.Lk)("div",{class:"name"},[(0,i.Lk)("label",null,[(0,i.Lk)("i",{class:"icon fas fa-volume-high"}),(0,i.eW)(" Volume ")]),(0,i.Lk)("br"),(0,i.Lk)("span",{class:"subtext"},[(0,i.Lk)("span",{class:"text"}," The volume to play the media resource at. ")])],-1))),_={class:"value"},A={class:"row item"},P=a((()=>(0,i.Lk)("div",{class:"name"},[(0,i.Lk)("label",null,[(0,i.Lk)("i",{class:"icon fas fa-bell"}),(0,i.eW)(" Snooze interval ")]),(0,i.Lk)("br"),(0,i.Lk)("span",{class:"subtext"},[(0,i.Lk)("span",{class:"text"}," How long the alarm should be paused after being triggered and manually snoozed. ")])],-1))),W={class:"value"},U={class:"row item"},R=a((()=>(0,i.Lk)("div",{class:"name"},[(0,i.Lk)("label",null,[(0,i.Lk)("i",{class:"icon fas fa-xmark"}),(0,i.eW)(" Dismiss timeout ")]),(0,i.Lk)("br"),(0,i.Lk)("span",{class:"subtext"},[(0,i.Lk)("span",{class:"text"}," How long the alarm should run before being automatically dismissed. ")])],-1))),N={class:"value"},H={class:"row item"},V=a((()=>(0,i.Lk)("div",{class:"name"},[(0,i.Lk)("label",null,[(0,i.Lk)("i",{class:"icon fas fa-play"}),(0,i.eW)(" Actions ")]),(0,i.Lk)("br"),(0,i.Lk)("span",{class:"subtext"},[(0,i.Lk)("span",{class:"text"}," Actions to perform when the alarm triggers. ")])],-1))),B={class:"value"};function z(e,t,n,a,p,z){const $=(0,i.g2)("Loading"),j=(0,i.g2)("CronEditor"),Y=(0,i.g2)("TimeInterval"),J=(0,i.g2)("FileSelector"),Z=(0,i.g2)("ToggleSwitch"),Q=(0,i.g2)("Slider"),G=(0,i.g2)("ActionsList");return(0,i.uX)(),(0,i.CE)("div",{class:(0,r.C4)(["alarm-editor-container",{"with-changes":z.hasChanges}])},[p.loading?((0,i.uX)(),(0,i.Wv)($,{key:0})):(0,i.Q3)("",!0),(0,i.Lk)("form",{class:"alarm-editor",onSubmit:t[14]||(t[14]=(0,o.D$)(((...e)=>z.save&&z.save(...e)),["prevent"]))},[(0,i.Lk)("div",s,[(0,i.Lk)("div",l,[(0,i.Lk)("div",u,[(0,i.bo)((0,i.Lk)("input",{type:"text",ref:"nameInput",placeholder:"Alarm name","onUpdate:modelValue":t[0]||(t[0]=e=>p.editForm.name=e)},null,512),[[o.Jo,p.editForm.name]])]),z.hasChanges?((0,i.uX)(),(0,i.CE)("div",c,[(0,i.Lk)("button",{type:"button",class:"reset-btn",title:"Reset",onClick:t[1]||(t[1]=e=>p.editForm={...n.value})},h),d])):(0,i.Q3)("",!0)])]),(0,i.Lk)("div",f,[(0,i.Lk)("div",m,[(0,i.Lk)("div",v,[y,g,k,(0,i.Lk)("div",b,[(0,i.Lk)("label",{class:(0,r.C4)({selected:"cron"===p.editForm.condition_type})},[(0,i.bo)((0,i.Lk)("input",{type:"radio",value:"cron","onUpdate:modelValue":t[2]||(t[2]=e=>p.editForm.condition_type=e)},null,512),[[o.XL,p.editForm.condition_type]]),(0,i.eW)("  Periodic ")],2),(0,i.eW)("   "),(0,i.Lk)("label",{class:(0,r.C4)({selected:"timestamp"===p.editForm.condition_type})},[(0,i.bo)((0,i.Lk)("input",{type:"radio",value:"timestamp","onUpdate:modelValue":t[3]||(t[3]=e=>p.editForm.condition_type=e)},null,512),[[o.XL,p.editForm.condition_type]]),(0,i.eW)("  Date/Time ")],2),(0,i.eW)("   "),(0,i.Lk)("label",{class:(0,r.C4)({selected:"interval"===p.editForm.condition_type})},[(0,i.bo)((0,i.Lk)("input",{type:"radio",value:"interval","onUpdate:modelValue":t[4]||(t[4]=e=>p.editForm.condition_type=e)},null,512),[[o.XL,p.editForm.condition_type]]),(0,i.eW)("  Timer ")],2)])]),(0,i.Lk)("div",x,["cron"===p.editForm.condition_type?((0,i.uX)(),(0,i.Wv)(j,{key:0,value:"cron"===n.value.condition_type?p.editForm.when:null,onInput:t[5]||(t[5]=e=>z.onWhenInput(e,"cron"))},null,8,["value"])):"timestamp"===p.editForm.condition_type?((0,i.uX)(),(0,i.CE)("input",{key:1,type:"datetime-local",value:"timestamp"===n.value.condition_type?p.editForm.when:null,onInput:t[6]||(t[6]=e=>z.onWhenInput(e.target.value,"timestamp"))},null,40,L)):"interval"===p.editForm.condition_type?((0,i.uX)(),(0,i.Wv)(Y,{key:2,value:"interval"===n.value.condition_type?p.editForm.when:null,onInput:t[7]||(t[7]=e=>z.onWhenInput(e,"interval"))},null,8,["value"])):(0,i.Q3)("",!0)])]),(0,i.Lk)("div",O,[S,(0,i.Lk)("div",X,[(0,i.bF)(J,{value:p.editForm.media,onInput:t[8]||(t[8]=e=>p.editForm.media=e)},null,8,["value"])])]),(0,i.Lk)("div",w,[T,(0,i.Lk)("div",D,[(0,i.bo)((0,i.Lk)("input",{type:"text","onUpdate:modelValue":t[9]||(t[9]=e=>p.editForm.media_plugin=e)},null,512),[[o.Jo,p.editForm.media_plugin]])])]),(0,i.Lk)("div",I,[(0,i.Lk)("label",null,[C,(0,i.Lk)("div",E,[(0,i.bF)(Z,{value:p.editForm.media_repeat,onInput:t[10]||(t[10]=e=>p.editForm.media_repeat=!!e.target.checked)},null,8,["value"])])])]),(0,i.Lk)("div",M,[F,(0,i.Lk)("div",_,[(0,i.bF)(Q,{value:z.audioVolume,range:[0,100],onChange:z.onVolumeChange},null,8,["value","onChange"])])]),(0,i.Lk)("div",A,[P,(0,i.Lk)("div",W,[(0,i.bF)(Y,{value:p.editForm.snooze_interval,onInput:t[11]||(t[11]=e=>p.editForm.snooze_interval=e)},null,8,["value"])])]),(0,i.Lk)("div",U,[R,(0,i.Lk)("div",N,[(0,i.bF)(Y,{value:p.editForm.dismiss_interval,onInput:t[12]||(t[12]=e=>p.editForm.dismiss_interval=e)},null,8,["value"])])]),(0,i.Lk)("div",H,[V,(0,i.Lk)("div",B,[(0,i.bF)(G,{value:z.procedure,onUpdate:t[13]||(t[13]=e=>z.onActionsUpdate(e))},null,8,["value"])])])])],32)],2)}var $=n(2423),j=n(9828),Y=n(1808);const J={class:"cron-editor-container"},Z=["textContent"],Q={class:"col-s-12 col-m-8"},G=["onUpdate:modelValue","onInput","onFocus"],K={class:"cron-description-container"},q=["textContent"],ee={key:1,class:"cron-description"},te=["textContent"],ne={key:0,class:"cron-next-run"},ie=["textContent"];function re(e,t,n,a,s,l){const u=(0,i.g2)("CopyButton");return(0,i.uX)(),(0,i.CE)("div",J,[(0,i.Lk)("div",{class:(0,r.C4)(["input-grid",{error:null!=s.error}])},[((0,i.uX)(!0),(0,i.CE)(i.FK,null,(0,i.pI)(s.labels,((e,n)=>((0,i.uX)(),(0,i.CE)("label",{class:(0,r.C4)(["item",{selected:s.selectedItem===n}]),key:n},[(0,i.Lk)("div",{class:"col-s-12 col-m-4",textContent:(0,r.v_)(e)},null,8,Z),(0,i.Lk)("div",Q,[(0,i.bo)((0,i.Lk)("input",{type:"text","onUpdate:modelValue":e=>s.cronExpr[n]=e,onKeydown:t[0]||(t[0]=(...e)=>l.validate&&l.validate(...e)),onInput:e=>l.updateCronExpr(n,e.target.value),onFocus:e=>s.selectedItem=n,onBlur:t[1]||(t[1]=e=>s.selectedItem=null)},null,40,G),[[o.Jo,s.cronExpr[n]]])])],2)))),128))],2),(0,i.Lk)("div",K,[s.error?((0,i.uX)(),(0,i.CE)("div",{key:0,class:"error",textContent:(0,r.v_)(s.error)},null,8,q)):((0,i.uX)(),(0,i.CE)("div",ee,[(0,i.bF)(u,{text:l.cronString},null,8,["text"]),(0,i.Lk)("div",{class:"cron-string",textContent:(0,r.v_)(l.cronString)},null,8,te),s.error?(0,i.Q3)("",!0):((0,i.uX)(),(0,i.CE)("div",ne,[(0,i.eW)(" Runs: "),(0,i.Lk)("span",{class:"cron-text",textContent:(0,r.v_)(s.cronDescription)},null,8,ie)]))]))])])}var oe=n(6590),ae=n.n(oe),se=n(9667),le={emits:["input"],components:{CopyButton:se.A},props:{value:{type:String,required:!0}},data(){return{cronExpr:this.value.split(/\s+/),cronDescription:null,error:null,selectedItem:null,cronRegex:new RegExp("^[0-9*/,-]*$"),labels:["Minute","Hour","Day of Month","Month","Day of Week"]}},computed:{cronString(){return this.cronExpr.map((e=>e.trim())).join(" ")}},watch:{cronExpr:{handler(e,t){e.forEach(((e,n)=>{e=e.trim(),e.match(this.cronRegex)?this.cronExpr[n]=e:this.cronExpr[n]=t[n]}))},deep:!0}},methods:{validate(e){const t=e.key;["Enter","Escape","Tab","ArrowLeft","ArrowRight","ArrowUp","ArrowDown","Backspace","Delete","Home","End"].includes(t)||e.ctrlKey||e.metaKey||t.match(this.cronRegex)||e.preventDefault()},updateCronDescription(){try{const e=ae().toString(this.cronString);this.error=null,this.cronDescription=e}catch(e){this.error=`Invalid cron expression: ${e}`,this.cronDescription=null}},updateCronExpr(e,t){this.cronExpr[e]=t,this.updateCronDescription(),this.error||this.$emit("input",this.cronString)}},mounted(){this.updateCronDescription()}},ue=n(6262);const ce=(0,ue.A)(le,[["render",re],["__scopeId","data-v-c55ac602"]]);var pe=ce;const he=e=>((0,i.Qi)("data-v-3daea642"),e=e(),(0,i.jt)(),e),de={class:"file-selector-container"},fe={class:"input"},me=["value","readonly"],ve=he((()=>(0,i.Lk)("i",{class:"fa fa-folder-open"},null,-1))),ye=[ve];function ge(e,t,n,r,o,a){const s=(0,i.g2)("Browser"),l=(0,i.g2)("Modal");return(0,i.uX)(),(0,i.CE)("div",de,[(0,i.Lk)("div",fe,[(0,i.Lk)("input",{type:"text",value:n.value,readonly:n.strict,onInput:t[0]||(t[0]=t=>e.$emit("input",t.target.value))},null,40,me),(0,i.Lk)("button",{type:"button",title:"Select a file",onClick:t[1]||(t[1]=t=>e.$refs.fileSelectorModal.show())},ye)]),(0,i.bF)(l,{title:"Select a file",ref:"fileSelectorModal"},{default:(0,i.k6)((()=>[(0,i.bF)(s,{initialPath:o.path,onInput:t[2]||(t[2]=e=>a.onValueChange(e)),onPathChange:t[3]||(t[3]=e=>o.path=e)},null,8,["initialPath"])])),_:1},512)])}var ke=n(9513),be=n(648),xe={emits:["input"],components:{Browser:be.A,Modal:ke.A},props:{value:{type:String},strict:{type:Boolean,default:!1}},data(){return{path:"/"}},methods:{onValueChange(e){this.$emit("input",e)},onFileSelect(e){null!=e&&(e.startsWith("/")||e.startsWith("file://"))?this.path=e.split("/").slice(0,-1).join("/"):this.path="/",this.$refs.fileSelectorModal.hide()}},watch:{value(e){this.onFileSelect(e)}},mounted(){this.onFileSelect(this.value)}};const Le=(0,ue.A)(xe,[["render",ge],["__scopeId","data-v-3daea642"]]);var Oe=Le;const Se={class:"time-interval-container"},Xe={class:"row"},we={class:"value-container"},Te=["step"],De={class:"unit-container"},Ie=["value"];function Ce(e,t,n,a,s,l){return(0,i.uX)(),(0,i.CE)("div",Se,[(0,i.Lk)("div",Xe,[(0,i.Lk)("div",we,[(0,i.bo)((0,i.Lk)("input",{type:"number","onUpdate:modelValue":t[0]||(t[0]=e=>s.duration=e),step:n.step},null,8,Te),[[o.Jo,s.duration]])]),(0,i.Lk)("div",De,[(0,i.bo)((0,i.Lk)("select",{"onUpdate:modelValue":t[1]||(t[1]=e=>s.selectedUnit=e)},[((0,i.uX)(!0),(0,i.CE)(i.FK,null,(0,i.pI)(s.units,(e=>((0,i.uX)(),(0,i.CE)("option",{key:e.value,value:e.value},(0,r.v_)(e.label),9,Ie)))),128))],512),[[o.u1,s.selectedUnit]])])])])}var Ee={emits:["input"],props:{value:{type:Number},step:{type:Number,default:1}},data(){return{duration:null,selectedUnit:"second",units:{second:{label:"Seconds",value:"second",multiplier:1},minute:{label:"Minutes",value:"minute",multiplier:60},hour:{label:"Hours",value:"hour",multiplier:3600},day:{label:"Days",value:"day",multiplier:86400}}}},computed:{unit(){return this.units[this.selectedUnit]},multiplier(){return this.unit.multiplier},seconds(){return null==this.duration?null:this.toSeconds(this.duration)}},watch:{seconds(e){null!==e&&(this.duration=this.toUnit(e),this.$emit("input",e))},value(e){this.duration=this.toUnit(e)}},methods:{toSeconds(e){return null==e?null:e*this.multiplier},toUnit(e){return null==e?null:e/this.multiplier}},mounted(){this.duration=this.toUnit(this.value)}};const Me=(0,ue.A)(Ee,[["render",Ce],["__scopeId","data-v-d1cb0878"]]);var Fe=Me,_e=n(11),Ae=n(2002),Pe={emits:["input"],mixins:[Ae.A],components:{ActionsList:$["default"],CronEditor:pe,FileSelector:Oe,Loading:j.A,Slider:Y.A,TimeInterval:Fe,ToggleSwitch:_e.A},props:{value:{type:Object,required:!0},newAlarm:{type:Boolean,default:!1}},data(){return{loading:!1,editForm:{...this.value}}},computed:{procedure(){return[...this.editForm.actions||[]]},audioVolume(){return this.editForm.audio_volume??this.defaultVolume},defaultVolume(){return this.$root.config?.alarm?.audio_volume??100},hasChanges(){return Object.keys(this.changes).length>0},changes(){const e={};return(this.value.audio_volume??this.defaultVolume)!==this.audioVolume&&(e.audio_volume=this.audioVolume),JSON.stringify(this.editForm.actions)!==JSON.stringify(this.value.actions)&&(e.actions=this.editForm.actions),["dismiss_interval","media","media_plugin","media_repeat","name","snooze_interval","when"].forEach((t=>{this.editForm[t]!==this.value[t]&&(e[t]=this.editForm[t])})),e}},methods:{actionsToArgs(e){return e?.map((e=>(e.name&&(e.action=e.name,delete e.name),e)))??[]},onWhenInput(e,t){if(null!=e){switch(t){case"timestamp":e=new Date(e).toISOString();break;case"cron":case"interval":break;default:return void console.error("Unknown cron type",t)}this.editForm.when=e,this.editForm.condition_type=t}},onActionsUpdate(e){e=[...e??[]],JSON.stringify(this.editForm.actions)!==JSON.stringify(e)&&(this.editForm.actions=e)},onVolumeChange(e){this.editForm.audio_volume=parseFloat(e.target.value)},async save(){this.loading=!0;let e={},t=null;this.newAlarm?(t="alarm.add",e={name:this.editForm.name,when:this.editForm.when,media:this.editForm.media,media_plugin:this.editForm.media_plugin,audio_volume:this.editForm.audio_volume,snooze_interval:this.editForm.snooze_interval,dismiss_interval:this.editForm.dismiss_interval,actions:this.actionsToArgs(this.editForm.actions)}):(t="alarm.edit",e={name:this.value.name,...this.changes},this.changes.actions&&(e.actions=this.actionsToArgs(this.changes.actions)),null!=this.changes.name&&(e.name=this.value.name,e.new_name=this.changes.name));try{const n=await this.request(t,e);this.$emit("input",n)}finally{this.loading=!1}}},mounted(){this.$nextTick((()=>{this.$refs.nameInput.focus()}))}};const We=(0,ue.A)(Pe,[["render",z],["__scopeId","data-v-5f15d80f"]]);var Ue=We}}]);
//# sourceMappingURL=7594.6acdb787.js.map