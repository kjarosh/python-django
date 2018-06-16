var elements = document.getElementsByClassName("select-section");

for(var i = 0; i < elements.length; i++){
	var el = elements[i];
	el.onchange = function(){
		if(el.value == '') return;
		
		url = el.dataset.urlformat.replace(el.dataset.urlreplace, el.value);
		window.location.href = url;
	}
}
