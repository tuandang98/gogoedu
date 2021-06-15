function reqListener () {
	/* no need to update game state with a 304 response */
	if (this.status == 304) return;
	
	/* the browser might return a cached 200 response even if 
	 * the server sent a 304. 
	 * if the last modified date has not changed there is no need for
	 * updating the game ui
	 */
	var lm = this.getResponseHeader("Last-Modified");
	if (lm == window.game_lm) return;
  
	window.game_lm = lm
	response = JSON.parse(this.responseText) 
	console.log(response);
	var current_player = null;
	for (playerID in response.players){
		player = response.players[playerID]
		element = document.getElementById(playerID)
		if (!element){
			/* if the card is not found then assume a new match has been started with new cards 
			 * and therefore reload the page
			 */
			location.reload();
			return;
		}
		if (player.is_current_player){
			current_player = player.name;
			element.style.backgroundColor = "red";
		}	
		else{
			element.style.backgroundColor = null;
		}
		element.textContent = player.name + ": " + player.score 
	}
	for (cardID in response.cards) {
		card = response.cards[cardID]
		element = document.getElementById(cardID)
		if (!element){
			/* if the card is not found then assume a new match has been started with new cards 
			 * and therefore reload the page
			 */
			location.reload();
			return;
		}
		element.innerHTML  = card.bgpos
		
		if (card.visible){
			element.style.visibility = "visible";
		}	
		else{
			element.style.visibility = "hidden";
		}
	}
	if(response.player){
		window.can_act = response.player.can_act
		window.should_refresh = response.player.should_refresh
	}
	element = document.getElementById("ended")
	if(response.status == "game ended"){
		element.style.visibility = "visible";
	}
	else{
		element.style.visibility = "hidden";
	}
	document.getElementById("message").textContent = response.message;
}

function refreshCallback(){
	if(window.should_refresh && !document.hidden){
		sendRequest();
	}
    setTimeout(refreshCallback, 1500);	
}

function sendRequest() {
	var oReq = new XMLHttpRequest();
	oReq.addEventListener("load", reqListener);
	oReq.open("GET", "json");
	oReq.setRequestHeader("Accept","application/json");
	if (window.game_lm){
		 oReq.setRequestHeader("If-Modified-Since", window.game_lm);
	}
	oReq.send();
}

function clickCard(e) {
	var form = document.getElementById("game-form");
	e.preventDefault();
	var params = "card="+this.value+"&csrfmiddlewaretoken="+form.elements.csrfmiddlewaretoken.value;
	var oReq = new XMLHttpRequest();
	oReq.addEventListener("load", reqListener);
	oReq.open("POST", "#");
	oReq.setRequestHeader("Accept","application/json");
	oReq.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	oReq.setRequestHeader("Content-length", params.length);
	oReq.send(params);
	return false;
}

function main(){
	var form = document.getElementById("game-form")
	window.game_lm = document.last_modified;
	form.onsubmit = function(e){e.preventDefault(); return false};
	for (name in form.elements) {
		var element = form.elements[name];
		if (element.type == "submit"){
			element.onclick = clickCard;
		}
	} 
	sendRequest();
    setTimeout(refreshCallback, 2000);
}