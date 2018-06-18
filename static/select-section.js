var elements = document.getElementsByClassName("select-section");

for(var i = 0; i < elements.length; i++){
	var el = elements[i];
	el.onchange = function(){
		if(el.value == ''){
			// global
			window.location.href = el.dataset.globalurlformat;
		}else{
			url = el.dataset.urlformat.replace(el.dataset.urlreplace, el.value);
			window.location.href = url;
		}
	}
}
