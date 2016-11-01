var https = require('https');
var fs = require('fs');
var readline = require('readline')
var async = require('async');

function replaceEmptySpace(str){
  var replaced = str.replace(/ /g, '%20');
  return replaced;
}

function identifyValidArticle(u,aName){
  https.get(u, (res) => {
    var data="";
    res.on('data', (chunk) => {
      data += chunk;
    });

    res.on('end', () => {
      var dataObj = JSON.parse(data)
      var htmlContent = dataObj.parse.text['*']

      function checkforDialogueOrLists(s){
        if (s.search("<blockquote") >= 0 || s.search("<dl") >= 0){
          return true;
        }
        else{
          return false;
        }
       }

      if (checkforDialogueOrLists(htmlContent) === false){
        fs.appendFileSync("validWiki.txt", aName + "\n", "UTF-8",{'flags': 'a'});
      }
    })
    res.on('error', (e) => {
    console.log("There was an error with:" + aName);
  });
})
}

function doSetTimeout(callback,u,i){
  setTimeout(function(){callback(u,i)},700)
}

//this initially goes through article list and writes the titles to articles that have no quote content
// var rdFile = readline.createInterface({
//     input: fs.createReadStream('./wikiArt.txt'),
//     output: process.stdout,
//     terminal: false
// });
//
// rdFile.on('line', function(line) {
//     urlA = "https://en.wikipedia.org/w/api.php?action=parse&format=json&page=" + replaceEmptySpace(line)
//     doSetTimeout(identifyValidArticle,urlA,line);
// });

function getWikipediaContent(i){
  https.get(i, (res) => {
    var data="";
    res.on('data', (chunk) => {
      data += chunk;
    });
    res.on('end', () => {
      function parseWikiData(dataInfo){
        dataInfo = JSON.parse(dataInfo)
        var pageid = Object.keys(dataInfo.query.pages)[0];
        return dataInfo.query.pages[pageid].extract
      }

      function cleanEntireContentString(str){
        str = str.split('= Notes =')[0]
          .split('= See also =')[0]
          .split('= References =')[0]
          .split('= Notes and references =')[0]
          .split('= Farthest South records =')[0]
          .split('= Reburial and commemorations =')[0]
          .split('= See alsoEdit =')[0]
          .split('= Bibliography =')[0]
          .split('= Modern editions =')[0]
          .split('= List of works =')[0]
          .split('= In popular culture =')[0]
          .split('= Works =')[0]
          .split('= Published texts =')[0]
          .split('= Books by Ellen Wilkinson =')[0]
          .replace(/ *\=.*\= */gi, "") //remove wiki titles
          .replace(/\=/gi, "") //remove remaining =
          .replace(/(\r\n|\n|\r)/gm, '') //remove new lines
          .replace( /([a-z|0-9|\)|\]])\.([A-Z])/g, "$1. $2") //seperates sentences with no space in between
        return str;
      }

      //break down long content string into seperate sentences
      var regexPrefix = "(Mrs\\.|Lt\\. Col\\.|Fr\\.|[Vv]ol\\.|i\\.e\\.|a\\.m\\.|p\\.m\\.|Nos\\.|Ch\\.|\\sal\\.\\s|Sgt\\.|Sen\\.|c\\.|\\sCol\\.\\s[A-Z]|Gens\\.|Repr\\.|Lt\\.|Dr\\.|St\\.|Mr\\.|Ms\\.|Cpt\\.|\\svs\\.|\\sed\\.|Gov\\.|\\sviz\\.|Adm\\.|Exe\\.|Rev\\.|Cpl\\.|Sr\\.|\\sv\\.|Jr\\.|Co\\.|Trans\\.|Maj\\.|Gen\\.|Brig\\.|Capt\\.|Ph\\.D\\.|Prof\\.|Ltd\\.|[Nn]o\\.|Kfz\\.|Sd\\.|[A-Z]\\.)"
      function contentToSentences(str){
      //  var re = /\b(\w\.\s)|(\.+\s[a-z])|(Mrs\.|Lt\. Col\.|Fr\.|Vol\.|i\.e\.|a\.m\.|p\.m\.|Nos\.|Ch\.|\sal\.\s|Sgt\.|Sen\.|c\.|\sCol\.\s[A-Z]|Gens\.|Repr\.|Lt\.|Dr\.|St\.|Mr\.|Ms\.|Cpt\.|\svs\.|\sed\.|Gov\.|\sviz\.|Adm\.|Exe\.|Rev\.|Cpl\.|Sr\.|\sv\.|Jr\.|Co\.|Trans\.|Maj\.|Gen\.|Brig\.|Capt\.|Ph\.D\.|Prof\.|Ltd\.|No\.\s|Kfz\.|Sd\.|[A-Z]\.)|([?|%[\.]|[0-9]\.|!|\.\"|"\.|\.])(\s+(?=[A-Z0-9]+)|(?=[A-Z]+))/g;
        var abbrev = "\\b(\\w\\.\\s)" //skips over abbreviations or single letters ex) J.
        var incorrectSent = "(\\.+\\s[a-z])" //skips over sentences with ... or with incorrect periods
        var sentenceIndentify = "([?|%[\\.]|[0-9]\\.|!|\\.\"|\"\\.|\\.])(\\s+(?=[A-Z0-9]+)|(?=[A-Z]+))"
        var re = new RegExp(abbrev+"|"+incorrectSent+"|"+regexPrefix+"|"+sentenceIndentify,"g")
        var result = str.replace(re, function(m, g1, g2, g3, g4){
          return g1 ? g1 : (g2 ? g2 : (g3 ? g3 : g4 + "\r"))
        });
        var sentencesArr = result.split("\r");
        return sentencesArr;
      }

      function removeOrFurtherCleanSentences(arr){
        var regExpOddASCII = /\(|\)|\[|\]|\"|\.\.\./g;
        var regExpNonASCII = /[^ -z]/g;
        var regAbbreviations = /([A-Z]{2,}|[A-Z]\.[A-Z])/g;
        var regCitations = /(London\:|Paris\:|New York\:|Antananarivo\:|London,|Hansard Vol\.|Oxford\:|Oxford,|Dunedin\:|Harlow\:|Auckland\:|Poetry\:|Collections,|Maine\:|\sed\.\s|Cambridge\:|Retrieved\s[0-1]|,\spp\.|Bonn\:|Accessed\s|et\sal\.)/g;
        var incorrectGrammar = /\s[a-z]+\.\s[a-z]+/g
        var j = 0;
        while (j < arr.length) {
          if (arr[j].match(regExpOddASCII) !== null || arr[j].match(regExpNonASCII) !== null || arr[j].match(regAbbreviations) !== null || arr[j].match(regCitations) !== null || arr[j].match(incorrectGrammar) !== null){
            arr.splice(j, 1);
          }
          else if(arr[j].charCodeAt(0) >= 97 && arr[j].charCodeAt(0) <= 122){
            arr.splice(j, 1);
          }
          else{
              j++;
          }
        }
        var finalFutherClean = []
        arr.forEach((sentence)=>{
          return cleanSentenceStuckTogether(sentence,finalFutherClean)
        })
        return finalFutherClean;
       }

      function cleanSentenceStuckTogether(str,arr){
       //var re = /(Mrs\.|Lt\. Col\.|Fr\.|Vol\.|i\.e\.|a\.m\.|p\.m\.|Nos\.|Ch\.|\sal\.\s|Sgt\.|Sen\.|c\.|\sCol\.\s[A-Z]|Gens\.|Repr\.|Lt\.|Dr\.|St\.|Mr\.|Ms\.|Cpt\.|\svs\.|\sed\.|Gov\.|\sviz\.|Adm\.|Exe\.|Rev\.|Cpl\.|Sr\.|\sv\.|Jr\.|Co\.|Trans\.|Maj\.|Gen\.|Brig\.|Capt\.|Ph\.D\.|Prof\.|Ltd\.|No\.\s|Kfz\.|Sd\.|[A-Z]\.)|([a-z]\.)(\s+(?=[A-Z0-9])|(?=[0-9]))|([0-9])(\s+(?=[A-Z0-9]))/g;
       var withSpaceBetween = "([a-z]\\.)(\\s+(?=[A-Z0-9])|(?=[0-9]))" //two sentence stuck with space between
       var noSpaceBetween = "([0-9]\\.)(\\s+(?=[A-Z0-9]))" // two sentences stuck together with no space
       var re = new RegExp(regexPrefix+"|"+withSpaceBetween+"|"+noSpaceBetween,"g")
       var result = str.replace(re, function(m, g1, g2, g3){
              return g1 ? g1 : (g2 ? g2 + "\r" : g3 + "\r")
       });
       var sentencesArr = result.split("\r");
       sentencesArr.forEach((sent)=>{
         arr.push(sent);
       })
       return arr;
      }

      function printWikiDataTextfile(){
          var content = parseWikiData(data)
          var entireContentAsStr = cleanEntireContentString(content)
          var sentencesList = removeOrFurtherCleanSentences(contentToSentences(entireContentAsStr))
          //start writing things here
          fs.appendFileSync("sentences.txt", sentencesList.join("\n"), "UTF-8",{'flags': 'a'});
          fs.appendFileSync("sentences.txt", "\n", "UTF-8",{'flags': 'a'});
      }
      printWikiDataTextfile();
    });
  });
}

console.log("**************************************************************************************************")
function gatherData(){
  var rd = readline.createInterface({
      input: fs.createReadStream('./validWiki.txt'),
      output: process.stdout,
      terminal: false
  });
  rd.on('line', function(line) {
      var updS = replaceEmptySpace(line)
      var url = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&explaintext=&titles=" + updS;
      doSetTimeout(getWikipediaContent,url);
  });
}

function removeDuplicateData(){
  var cd = readline.createInterface({
      input: fs.createReadStream('./sentences.txt'),
      output: process.stdout,
      terminal: false
  });
  var obj = {}
  cd.on('line', function(line) {
    if(obj[line]===undefined){
      obj[line] = line
      fs.appendFileSync("allWikipediaSentences.txt", obj[line]+"\n", "UTF-8",{'flags': 'a'});
    }
  });
}

gatherData();
setTimeout(removeDuplicateData,5000)
