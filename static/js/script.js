const words = ["for all your needs", "your one market place", "where you find best deals"];
let i = 0;
let timer;

function typingEffect() {
	let word = words[i].split("");
	var loopTyping = function() {
		if (word.length > 0) {
			document.getElementById('word').innerHTML += word.shift();
		} else {
			deletingEffect();
			return false;
		};
		timer = setTimeout(loopTyping, 100);
	};
	loopTyping();
};

function deletingEffect() {
	let word = words[i].split("");
	var loopDeleting = function() {
		if (word.length > 0) {
			word.pop();
			document.getElementById('word').innerHTML = word.join("");
		} else {
			if (words.length > (i + 1)) {
				i++;
			} else {
				i = 0;
			};
			typingEffect();
			return false;
		};
		timer = setTimeout(loopDeleting, 200);
	};
	loopDeleting();
};

typingEffect();

window.addEventListener('scroll',()=>{
	let content = document.querySelector('.container-fluid');
	let contentPosition = content.getBoundingClientRect().top;
	let screenPosition = window.innerHeight;
	if (contentPosition < screenPosition){
		content.classList.add('active');
	} else{
		content.classList.remove('active');
	}
});

window.addEventListener('scroll',()=>{
	let content = document.querySelector('.container-fluid-2');
	let contentPosition = content.getBoundingClientRect().top;
	let screenPosition = window.innerHeight;
	if (contentPosition < screenPosition){
		content.classList.add('active');
	} else{
		content.classList.remove('active');
	}
});

window.addEventListener('scroll',()=>{
	let content = document.querySelector('.container-fluid-3');
	let contentPosition = content.getBoundingClientRect().top;
	let screenPosition = window.innerHeight;
	if (contentPosition < screenPosition){
		content.classList.add('active');
	} else{
		content.classList.remove('active');
	}
});