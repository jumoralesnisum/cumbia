//
// Place any custom JS here
//
function enviar() {
    let texto = document.getElementById('texto').value
    let modo = document.getElementById('modo').value
    let language = document.getElementById('idioma').value
    let space = document.getElementById('space')
fetch((language=='es')?'/predecir':'/predict', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ "text": texto, "index": modo})
})
   .then(response => response.json())
   .then(response => response.value.text)
   .then(response => beforeAlert(response))
}
function traducir() {
    translate('lbltexto', 'Cuéntenos, cómo podemos ayudarle?','How can we help you?')
    translate('h1', 'Categorización de Información', 'Text Classification')
    translate('textoHelp', 'Escriba aquí su historia','Tell us your story')
    translate('explanation', 'Escriba en el formulario el texto que desea categorizar', 'Write on the form the text you want to classify')
    translate('btnSend','Enviar','Send')
    translate('lblMode','Modo','Mode')
    translate('lblLang','Idioma','Language')
    translate('opt2','Clásico','Classical')
    translate('opt3','LLM Entrenado','Trained LLM')
    return true
}
function beforeAlert(response) {
    let language = document.getElementById('idioma').value
    let text1= (language=='es')?'Respuesta':'Result'
    let text2 = (language=='es')?'Resultado de la clasificación':'Classification result'
    createAlert(text1,text2,response, 'success', true,true,'pageMessages')
}
function translate(id, spanish, english) {
    let language = document.getElementById('idioma').value
    let elem = document.getElementById(id)
    elem.innerText = (language=='es')?spanish:english
}
function createAlert(title, summary, details, severity, dismissible, autoDismiss, appendToId) {
  var iconMap = {
    info: "fa fa-info-circle",
    success: "fa fa-thumbs-up",
    warning: "fa fa-exclamation-triangle",
    danger: "fa ffa fa-exclamation-circle"
  };

    let iconAdded = false;

    const alertClasses = ["alert", "animated", "flipInX"];
    alertClasses.push("alert-" + severity.toLowerCase());

  if (dismissible) {
    alertClasses.push("alert-dismissible");
  }

    const msgIcon = $("<i />", {
        "class": iconMap[severity] // you need to quote "class" since it's a reserved keyword
    });

    const msg = $("<div />", {
        "class": alertClasses.join(" ") // you need to quote "class" since it's a reserved keyword
    });

    if (title) {
        const msgTitle = $("<h4 />", {
            html: title
        }).appendTo(msg);

        if(!iconAdded){
      msgTitle.prepend(msgIcon);
      iconAdded = true;
    }
  }

  if (summary) {
    var msgSummary = $("<strong />", {
      html: summary
    }).appendTo(msg);

    if(!iconAdded){
      msgSummary.prepend(msgIcon);
      iconAdded = true;
    }
  }

  if (details) {
    var msgDetails = $("<p />", {
      html: details
    }).appendTo(msg);

    if(!iconAdded){
      msgDetails.prepend(msgIcon);
      iconAdded = true;
    }
  }


  if (dismissible) {
    var msgClose = $("<span />", {
      "class": "close", // you need to quote "class" since it's a reserved keyword
      "data-dismiss": "alert",
      html: "<i class='fa fa-times-circle'></i>"
    }).appendTo(msg);
  }

  $('#' + appendToId).prepend(msg);

  if(autoDismiss){
    setTimeout(function(){
      msg.addClass("flipOutX");
      setTimeout(function(){
        msg.remove();
      },1000);
    }, 5000);
  }
}