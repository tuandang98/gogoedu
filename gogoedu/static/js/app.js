const localStorage = window.localStorage || {
  getItem: () => null,
  setItem: () => {},
  clear: () => {},
};

const ALL_KANA = {
  hiragana: {
    monographs: {
      "あ" : ["a"],
      "い" : ["i"],
      "う" : ["u"],
      "え" : ["e"],
      "お" : ["o"],
      "か" : ["ka"],
      "き" : ["ki"],
      "く" : ["ku"],
      "け" : ["ke"],
      "こ" : ["ko"],
      "さ" : ["sa"],
      "し" : ["shi"],
      "す" : ["su"],
      "せ" : ["se"],
      "そ" : ["so"],
      "た" : ["ta"],
      "ち" : ["chi"],
      "つ" : ["tsu"],
      "て" : ["te"],
      "と" : ["to"],
      "な" : ["na"],
      "に" : ["ni"],
      "ぬ" : ["nu"],
      "ね" : ["ne"],
      "の" : ["no"],
      "は" : ["ha", "wa"], //the latter as particle
      "ひ" : ["hi"],
      "ふ" : ["fu"],
      "へ" : ["he", "e"], //the latter as particle
      "ほ" : ["ho"],
      "ま" : ["ma"],
      "み" : ["mi"],
      "む" : ["mu"],
      "め" : ["me"],
      "も" : ["mo"],
      "や" : ["ya"],
      "ゆ" : ["yu"],
      "よ" : ["yo"],
      "ら" : ["ra"],
      "り" : ["ri"],
      "る" : ["ru"],
      "れ" : ["re"],
      "ろ" : ["ro"],
      "わ" : ["wa"],
      "を" : ["wo"],
      "ん" : ["n"]
    },
    monographs_diacritics: {
      "が" : ["ga"],
      "ぎ" : ["gi"],
      "ぐ" : ["gu"],
      "げ" : ["ge"],
      "ご" : ["go"],
      "ざ" : ["za"],
      "じ" : ["ji"],
      "ず" : ["zu"],
      "ぜ" : ["ze"],
      "ぞ" : ["zo"],
      "だ" : ["da"],
      "ぢ" : ["ji", "dji", "jyi"],
      "づ" : ["dzu", "zu"],
      "で" : ["de"],
      "ど" : ["do"],
      "ば" : ["ba"],
      "び" : ["bi"],
      "ぶ" : ["bu"],
      "べ" : ["be"],
      "ぼ" : ["bo"],
      "ぱ" : ["pa"],
      "ぴ" : ["pi"],
      "ぷ" : ["pu"],
      "ぺ" : ["pe"],
      "ぽ" : ["po"]
    },
    digraphs: {
      "きゃ" : ["kya"],
      "きゅ" : ["kyu"],
      "きょ" : ["kyo"],
      "しゃ" : ["sha"],
      "しゅ" : ["shu"],
      "しょ" : ["sho"],
      "ちゃ" : ["cha"],
      "ちゅ" : ["chu"],
      "ちょ" : ["cho"],
      "にゃ" : ["nya"],
      "にゅ" : ["nyu"],
      "にょ" : ["nyo"],
      "ひゃ" : ["hya"],
      "ひゅ" : ["hyu"],
      "ひょ" : ["hyo"],
      "みゃ" : ["mya"],
      "みゅ" : ["myu"],
      "みょ" : ["myo"],
      "りゃ" : ["rya"],
      "りゅ" : ["ryu"],
      "りょ" : ["ryo"]
    },
    digraphs_diacritics: {
      "ぎゃ" : ["gya"],
      "ぎゅ" : ["gyu"],
      "ぎょ" : ["gyo"],
      "じゃ" : ["ja"],
      "じゅ" : ["ju"],
      "じょ" : ["jo"],
      "びゃ" : ["bya"],
      "びゅ" : ["byu"],
      "びょ" : ["byo"],
      "ぴゃ" : ["pya"],
      "ぴゅ" : ["pyu"],
      "ぴょ" : ["pyo"]
    },
    
  },
  katakana: {
    monographs: {
      "ア" : ["a"],
      "イ" : ["i"],
      "ウ" : ["u"],
      "エ" : ["e"],
      "オ" : ["o"],
      "カ" : ["ka"],
      "キ" : ["ki"],
      "ク" : ["ku"],
      "ケ" : ["ke"],
      "コ" : ["ko"],
      "サ" : ["sa"],
      "シ" : ["shi"],
      "ス" : ["su"],
      "セ" : ["se"],
      "ソ" : ["so"],
      "タ" : ["ta"],
      "チ" : ["chi"],
      "ツ" : ["tsu"],
      "テ" : ["te"],
      "ト" : ["to"],
      "ナ" : ["na"],
      "ニ" : ["ni"],
      "ヌ" : ["nu"],
      "ネ" : ["ne"],
      "ノ" : ["no"],
      "ハ" : ["ha"],
      "ヒ" : ["hi"],
      "フ" : ["fu"],
      "ヘ" : ["he"],
      "ホ" : ["ho"],
      "マ" : ["ma"],
      "ミ" : ["mi"],
      "ム" : ["mu"],
      "メ" : ["me"],
      "モ" : ["mo"],
      "ヤ" : ["ya"],
      "ユ" : ["yu"],
      "ヨ" : ["yo"],
      "ラ" : ["ra"],
      "リ" : ["ri"],
      "ル" : ["ru"],
      "レ" : ["re"],
      "ロ" : ["ro"],
      "ワ" : ["wa"],
      "ヲ" : ["wo"],
      "ン" : ["n"]
    },
    monographs_diacritics: {
      "ガ" : ["ga"],
      "ギ" : ["gi"],
      "グ" : ["gu"],
      "ゲ" : ["ge"],
      "ゴ" : ["go"],
      "ザ" : ["za"],
      "ジ" : ["ji"],
      "ズ" : ["zu"],
      "ゼ" : ["ze"],
      "ゾ" : ["zo"],
      "ダ" : ["da"],
      "ヂ" : ["ji"],
      "ヅ" : ["zu"],
      "デ" : ["de"],
      "ド" : ["do"],
      "バ" : ["ba"],
      "ビ" : ["bi"],
      "ブ" : ["bu"],
      "ベ" : ["be"],
      "ボ" : ["bo"],
      "パ" : ["pa"],
      "ピ" : ["pi"],
      "プ" : ["pu"],
      "ペ" : ["pe"],
      "ポ" : ["po"]
    },
    digraphs: {
      "キャ" : ["kya"],
      "キュ" : ["kyu"],
      "キョ" : ["kyo"],
      "シャ" : ["sha"],
      "シュ" : ["shu"],
      "ショ" : ["sho"],
      "チャ" : ["cha"],
      "チュ" : ["chu"],
      "チョ" : ["cho"],
      "ニャ" : ["nya"],
      "ニュ" : ["nyu"],
      "ニョ" : ["nyo"],
      "ヒャ" : ["hya"],
      "ヒュ" : ["hyu"],
      "ヒョ" : ["hyo"],
      "ミャ" : ["mya"],
      "ミュ" : ["myu"],
      "ミョ" : ["myo"],
      "リャ" : ["rya"],
      "リュ" : ["ryu"],
      "リョ" : ["ryo"]
    },
    digraphs_diacritics: {
      "ギャ" : ["gya"],
      "ギュ" : ["gyu"],
      "ギョ" : ["gyo"],
      "ジャ" : ["ja"],
      "ジュ" : ["ju"],
      "ジョ" : ["jo"],
      "ヂャ" : ["ja"],
      "ヂュ" : ["ju"],
      "ヂョ" : ["jo"],
      "ビャ" : ["bya"],
      "ビュ" : ["byu"],
      "ビョ" : ["byo"],
      "ピャ" : ["pya"],
      "ピュ" : ["pyu"],
      "ピョ" : ["pyo"]
    },
    
  }
}

function init() {
  loadTemplates();
  runGame();
}

function loadTemplates() {
  document.templates = {};
  for (let template of document.getElementsByTagName('template')) {
    document.templates[template.getAttribute('id')] = document.importNode(template, true).content;
  }
}

function runGame() {
  let timerElement = document.getElementById('timer');
  let answerFieldElement = document.getElementById('answer_field');
  let currentKanaElement = document.getElementById('current_kana');


  let kanaSettings = {};
  for (let type in ALL_KANA) {
    for (let subtype in ALL_KANA[type]) {
      kanaSettings[type + '_' + subtype] = false;
    }
  }

  let gameSettings;
  let storedKanaSettings = localStorage.getItem('kanaSettings');
  gameSettings = new GameSettings(
    timerElement,
    answerFieldElement,
    currentKanaElement,
    document.getElementById('lastScore'),
    JSON.parse(storedKanaSettings) || kanaSettings
  );

  let storedStats = localStorage.getItem('kanaStats');
  let kanaStats = JSON.parse(storedStats) || {};

  window.game = new KanaGemu(ALL_KANA, gameSettings, kanaStats);
}

function reset() {
  localStorage.clear();
  window.location.reload();
}

class KanaGemu {
  constructor(allKana, gameSettings, kanaStats) {
    this.allKana = allKana;
    this.gameSettings = gameSettings;
    this.kanaStats = kanaStats;
    this.challangeStartTime = 0;
    this.generateKanaMap();

    //Set up setting elements
    let settingsElement = document.getElementById('settings_kana');
    settingsElement.addEventListener('input',
    (ev) => this.settingsChangeListener(ev, this)
  );

  //Remove any children from the settings element
  while(settingsElement.firstChild) {
    settingsElement.removeChild(settingsElement.firstChild);
  }

  //Collect all setting elements in a dom fragment first
  let domFragment = document.createDocumentFragment();
  for (let key in this.gameSettings.kanaSettings) {
    let newSetting = new SettingsElement(key, this.gameSettings.kanaSettings[key]);
    settingsElement.appendChild(newSetting.mainNode);
    this.gameSettings.addSettingsElement(key, newSetting);
  }

  //Actually attach settings in DOM
  settingsElement.appendChild(domFragment);

  this.nextKana();

  this.timerInterval = setInterval(this.updateTime, 43, this);
  this.registerAnswerEventHandler();
  this.gameSettings.answerFieldElement.addEventListener('focus', () => this.nextKana());
}

checkAnswer(answer) {
  if (this.flatKanaAnswerMap[this.curKanaChallange].includes(answer)) {
    let score = 1 + (100 / ((Date.now() - game.challangeStartTime) / 1000));
    score = Math.min(100, score);
    this.updateStats(this.curKanaChallange, score);
    this.nextKana();
  }
}

updateStats(kana, score) {
  if (typeof this.kanaStats[this.curKanaChallange] !== 'undefined') {
    let newScore = (this.kanaStats[this.curKanaChallange] * 9 + score) / 10;
    this.kanaStats[this.curKanaChallange] = newScore;
  }
  else {
    this.kanaStats[this.curKanaChallange] = score;
  }
  this.gameSettings.lastScoreElement.textContent = score.toFixed(2).toString();
  localStorage.setItem('kanaStats', JSON.stringify(this.kanaStats));
}

persistGameSettings() {
  localStorage.setItem('kanaSettings', JSON.stringify(this.gameSettings.kanaSettings));
}

nextKana() {
  this.challangeStartTime = Date.now();
  let scoreMap = {};
  let curScore = 100;
  let curKana = null;
  for (let kanaKey in this.activeKana) {
    let score = this.kanaStats[this.activeKana[kanaKey]] || 0;
    let rand = (Math.random() * 900 + 1);

    score = (score + rand) / 10;
    scoreMap[this.activeKana[kanaKey]] = score;
  }

  for (let key in scoreMap) {
    if (scoreMap[key] < curScore) {
      curScore = scoreMap[key];
      curKana = key;
    }
  }

  this.curKanaChallange = curKana;
  this.gameSettings.currentKanaElement.textContent = curKana;
  this.gameSettings.answerFieldElement.textContent = '';
  console.log(this.flatKanaAnswerMap[curKana] || '');
}

generateKanaMap() {
  this.flatKanaAnswerMap = {};
  if (this.gameSettings.kanaSettings.hiragana_monographs) {
    this.flatKanaAnswerMap = {...this.flatKanaAnswerMap, ...this.allKana.hiragana.monographs}
  }
  if (this.gameSettings.kanaSettings.hiragana_monographs_diacritics) {
    this.flatKanaAnswerMap = {...this.flatKanaAnswerMap, ...this.allKana.hiragana.monographs_diacritics}
  }
  if (this.gameSettings.kanaSettings.hiragana_digraphs) {
    this.flatKanaAnswerMap = {...this.flatKanaAnswerMap, ...this.allKana.hiragana.digraphs}
  }
  if (this.gameSettings.kanaSettings.hiragana_digraphs_diacritics) {
    this.flatKanaAnswerMap = {...this.flatKanaAnswerMap, ...this.allKana.hiragana.digraphs_diacritics}
  }
  if (this.gameSettings.kanaSettings.hiragana_obsolete) {
    this.flatKanaAnswerMap = {...this.flatKanaAnswerMap, ...this.allKana.hiragana.obsolete}
  }
  if (this.gameSettings.kanaSettings.katakana_monographs) {
    this.flatKanaAnswerMap = {...this.flatKanaAnswerMap, ...this.allKana.katakana.monographs}
  }
  if (this.gameSettings.kanaSettings.katakana_monographs_diacritics) {
    this.flatKanaAnswerMap = {...this.flatKanaAnswerMap, ...this.allKana.katakana.monographs_diacritics}
  }
  if (this.gameSettings.kanaSettings.katakana_digraphs) {
    this.flatKanaAnswerMap = {...this.flatKanaAnswerMap, ...this.allKana.katakana.digraphs}
  }
  if (this.gameSettings.kanaSettings.katakana_digraphs_diacritics) {
    this.flatKanaAnswerMap = {...this.flatKanaAnswerMap, ...this.allKana.katakana.digraphs_diacritics}
  }
  if (this.gameSettings.kanaSettings.katakana_obsolete) {
    this.flatKanaAnswerMap = {...this.flatKanaAnswerMap, ...this.allKana.katakana.obsolete}
  }

 

  this.activeKana = Object.keys(this.flatKanaAnswerMap);
}

settingsChangeListener(ev, game) {
  ev.stopPropagation();
  for (let settingKey in game.gameSettings.kanaSettings) {
    let settingsElement = game.gameSettings.getSettingsElement(settingKey);
    if (game.gameSettings.kanaSettings[settingKey] !== settingsElement.isActive) {
      game.gameSettings.kanaSettings[settingKey] = settingsElement.isActive;
    }
  }
  game.generateKanaMap();
  game.persistGameSettings();
}

answerFieldEventHandler(ev, game) {
  game.checkAnswer(ev.target.innerText.trim())
}

registerAnswerEventHandler() {
  this.gameSettings.answerFieldElement.addEventListener('input',
  this.eventHandlerRef = (ev) => this.answerFieldEventHandler(ev, this)
);
}

removeAnswerEventHandler() {
  this.gameSettings.answerFieldElement.removeEventListener('input', this.eventHandlerRef);
}

async updateTime(game) {
  game.gameSettings.timerElement.textContent = ((Date.now() - game.challangeStartTime) / 1000)
  .toFixed(2).toString().padStart(5, '0');
}
}

class GameSettings {
  constructor(timerElement, answerFieldElement, currentKanaElement, lastScoreElement, kanaSettings) {
    this.timerElement = timerElement;
    this.answerFieldElement = answerFieldElement;
    this.currentKanaElement = currentKanaElement;
    this.lastScoreElement = lastScoreElement;
    this.kanaSettings = kanaSettings;
    this.settingsElements = {};
  }

  addSettingsElement(key, element) {
    this.settingsElements[key] = element;
  }

  getSettingsElement(key) {
    return this.settingsElements[key];
  }
}

class SettingsElement {
  constructor(settingKey, settingActive = false) {
    this._mainNode = document.templates.settings_input.firstElementChild.cloneNode(true);
    this._checkboxNode = this.mainNode.getElementsByTagName('input')[0];
    this._labelNode = this.mainNode.getElementsByTagName('label')[0];
    this._checkboxNode.setAttribute('id', settingKey);
    this._checkboxNode.checked = settingActive;
    this._labelNode.setAttribute('for', settingKey);
    this._labelNode.textContent = settingKey.replace(/_/gi, ' ');
  }

  get mainNode() {
    return this._mainNode;
  }

  set mainNode(v) {
    if (this._mainNode !== null) {
      this._mainNode = v;
    } else {
      throw 'Cannot overwrite node of SettingsElement';
    }
  }

  get isActive() {
    return this._checkboxNode.checked;
  }
}
