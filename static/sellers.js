var sellerInfo = {
	"addHook": function() {
		if (window.addEventListener) {
			window.addEventListener('load', sellerInfo.init, false);
		} else if (window.attachEvent) {
			window.attachEvent('onload', sellerInfo.init);
		}
	},
	"init": function() {
		if (!sellerInfo.isPresent()) {
			sellerInfo.load();
		}
	},
	"isPresent": function() {
		var elements = document.getElementsByClassName('sellers');
		if (elements.length == 0)
			return false;
		var container = elements[0];
		var sellers = container.getElementsByClassName('seller');
		return sellers.length > 0;
	},
	"load": function() {
		var httpRequest;
		if (window.XMLHttpRequest) {
			httpRequest = new XMLHttpRequest;
		} else if (window.ActiveXObject) {
			httpRequest = new ActiveXObject("Microsoft.XMLHTTP");
		}
		httpRequest.onreadystatechange = function() {
			if (httpRequest.readyState == 4) {
				if (httpRequest.status === 200) {
					sellerInfo.ajaxLoaded(httpRequest);
				} else if (httpRequest.status / 100 == 4) {
					// client error, stop
				} else {
					sellerInfo.ajaxFailed(httpRequest);
				}
			}
		};
		var loc = window.location;
		var url = loc.protocol+'//'+loc.host+loc.pathname+'/sellers';
		httpRequest.open('GET', url, true);
		httpRequest.setRequestHeader('Accept', 'text/html');
		httpRequest.send(null);
	},
	"ajaxLoaded":function(httpRequest) {
		var data = httpRequest.responseText;
		var elements = document.getElementsByClassName('sellers');
		if (elements.length == 0)
			return false;
		var container = elements[0];
		container.innerHTML = data;
	},
	"ajaxFailed":function(httpRequest) {
		window.timeout(sellerInfo.load, 2000);
	}
};

sellerInfo.addHook();
