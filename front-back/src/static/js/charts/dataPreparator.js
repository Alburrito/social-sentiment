function prepareRecordsData(records){
    records = records.replace(/&#34;/g,'"');
    records = JSON.parse(records);
  
    score_records = records.score_records;
    foll_records = records.foll_records;
    fav_records = records.fav_records;
    eng_records = records.eng_records;
  
    score_records.forEach(element => {
        element.date = new Date(element.date + "Z");
    });
  
    foll_records.forEach(element => {
        element.date = new Date(element.date + "Z");
    });
  
    fav_records.forEach(element => {
        element.date = new Date(element.date + "Z");
    });
  
    eng_records.forEach(element => {
        element.date = new Date(element.date + "Z");
    });
  
    comparator_records = [];
    for (let i = 0; i < score_records.length; i++) {
      comparator_records.push({
        date : score_records[i].date,
        score : score_records[i].value,
        followers : foll_records[i].value,
        favourites : fav_records[i].value,
        engagement : eng_records[i].value
      });
    }
    
    return score_records, foll_records, fav_records, eng_records, comparator_records;
}

function prepareSentimentData(sentimentData){
    sentimentData = sentimentData.replace(/&#34;/g,'"');
    sentimentData = JSON.parse(sentimentData);

    generalData = sentimentData.general;
    recentData = sentimentData.recent;
    sent_records = sentimentData.records.sent_records;

    return generalData, recentData, sent_records;
}