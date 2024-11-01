const id_progress_receipt='id_upload_progress_receipt';
const id_progress_inquiry='id_progress_inquiry';
const id_progress_analyzeCommand='id_analyzeCommand_progress';
const id_preview_receipt='preview_receipt';
const id_chat_app_container='chat_app_row_list';
const bot_name='Vinx';
var   chatbotContextLoaded=false;

let rowindex=0;

function isNullOrEmpty(str) {
    return !str || str.trim() === "";
}
function fillMessage(template, data) {
    return template.replace(/{(\w+)}/g, (match, key) => data[key] || '');
}

function updateProgress(id_progress, percentage, automatic_forward) {
          if (percentage>0&&percentage<100)
                $("#"+id_progress).show();
          else {
                $("#"+id_progress).hide();
                return;
           }
          $("#"+id_progress).children().attr("aria-valuenow",percentage);
          $("#"+id_progress).children().width(percentage+"%");
          if (automatic_forward&&automatic_forward==true&&(percentage+7)<100) {
                setTimeout(() => {
                    updateProgress(id_progress, percentage+7, automatic_forward);
                }, "1200");
          }
}
function pushHandlebarsTemplate(data,section_row,section_append ) {
      if (!section_append) {
          section_append=section_row+"_list";
          section_row+="_template";
      }
      let templateSource=$("#"+section_row)[0].innerHTML;
      let templateTarget=Handlebars.compile(templateSource);
      let contentTarget=templateTarget(data);
      $("#no_rows").remove();
      $("#"+section_append).append(contentTarget);
}
Handlebars.registerHelper("inc", function(options)
{
    return ++rowindex;
});
Handlebars.registerHelper("getIndex", function( options)
{
    return rowindex;
});
Handlebars.registerHelper('isEven', function(value, options) {
      if (rowindex % 2 === 0) {
        return options.fn(this);
      } else {
        return options.inverse(this);
      }
 });

// Registra l'helper per formattare le date
Handlebars.registerHelper('dateFormat', function(date, format) {
            const momentDate = moment(date);
            const hours = momentDate.hours();
            if (hours === 0) {
                return momentDate.format(format);
            } else {
                return momentDate.format("MM/DD/YYYY HH:mm");
            }
});

function deleteReceiptById(id) {
      var elem = document.getElementById(id);
      return elem.parentNode.removeChild(elem);
}
function sendReceipt() {
      console.log("submitted");
       var form = $('#receiptForm')[0];
       var data = new FormData(form);
       updateProgress(id_progress_receipt,"5",true);
     $.ajax( {
       url: '/sendReceipt',
       enctype: 'multipart/form-data',
       headers: {
               'Access-Control-Allow-Origin': '*',
       },
       type: 'POST',
       data: data,
       processData: false,
       contentType: false,
       beforeSend: function( xhr ) {
           updateProgress(id_progress_receipt,"0",true);
       },
       success: function(data){
                  updateProgress(id_progress_receipt,"100");
                  pushHandlebarsTemplate(data,'receipt_row')
       },
        complete: function(data) {
           updateProgress(id_progress_receipt,"0");
           var preview = document.getElementById(id_preview_receipt);
           preview.src='';
           $("#receipt-image").val('');
        }
     } );
}

function goMenu(id) {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
            const page = link.getAttribute('data-bs-target').substring(1);
            if (page==id) {
                link.click();
            }
     });
}

function preparePreview(obj) {
          const [file] = obj.files;
          console.log("file");
          if (file) {
            var preview = document.getElementById(id_preview_receipt);
            console.log('Preview:'+preview);
            preview.src = URL.createObjectURL(file)
          }
}
//######################################################
//                  Script per Chat Q&A                #
//######################################################
function importData() {
  let input = document.createElement('input');
  input.type = 'file';
  input.name = 'QA-file';
  input.accept = 'application/pdf';
  input.onchange = _ => {
    // Usa il metodo per leggere il file selezionato ed innsescare l'invio al server per l'elaborazione
            let files =   Array.from(input.files);
            console.log(files);
            sendContext(input);
        };
  input.click();

}
// Invia messaggio per bot
function sendChatBotMessage(message) {
       data = {
         'message':message,
         'bot_name':bot_name
       }
       pushHandlebarsTemplate(data,'chat_bot_row_template',id_chat_app_container);
       scrollToBottomChatContainer();
}
// Invia messaggio per guest
function sendGuestMessage(message) {
       data = {
         'message':message,
       }
       pushHandlebarsTemplate(data,'guest_row_template',id_chat_app_container);
       $('#guestInput').val('');
       scrollToBottomChatContainer();
}
// Scrolla in fondo alla lista  ad ogni nuovo invio di messaggio
function scrollToBottomChatContainer() {
    var chatContainer = document.getElementById(id_chat_app_container);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}
function sendContext(fileInput) {
       console.log("submitted");
       var form = document.createElement('form');
       form.appendChild(fileInput);
       form.setAttribute('method', 'post');
       var data = new FormData(form);
     $.ajax( {
       url: '/sendContext',
       type: 'POST',
       enctype: 'multipart/form-data',
       headers: {
               'Access-Control-Allow-Origin': '*',
       },
       data: data,
       processData: false,
       contentType: false,
       beforeSend: function( xhr ) {
           updateProgress(id_progress_inquiry,"0",true);
       },
       success: function(data){
                  updateProgress(id_progress_inquiry,"100");
                  if (data && data.status && data.status=='OK') {
                        prepareResponseForFileAcquisition(data);
                        chatbotContextLoaded=true;
                  } else {
                        sendChatBotMessage(messages[data.reason]);
                  }
       },
        complete: function(data) {
           updateProgress(id_progress_inquiry,"0");
        }
     } );
}
function prepareResponseForFileAcquisition(data) {
        var message='';
        message=fillMessage(messages.file_acquired, data);
        sendChatBotMessage(message);
}
function answerQuestion(question) {
       if (isNullOrEmpty(question)) {
            sendChatBotMessage(messages.no_empty_text);
            return;
       } else
            sendGuestMessage(question);

       if (!chatbotContextLoaded) {
            sendChatBotMessage(messages.context_is_missing);
            return;
       }
       console.log("submitted");
       data = {
            'QA-question':question
       };

     $.ajax( {
       url: '/answerQuestion?QA-question='+question,
       type: 'GET',
       headers: {
               'Access-Control-Allow-Origin': '*',
       },
       data: data,
       processData: false,
       contentType: false,
       beforeSend: function( xhr ) {
           updateProgress(id_progress_inquiry,"0",true);
       },
       success: function(data){
                  updateProgress(id_progress_inquiry,"100");
                  if (data && data.status && data.status=='OK') {
                        prepareResponseForAnwser(data);
                  } else {
                        sendChatBotMessage(messages[data.reason]);
                  }
       },
        complete: function(data) {
           updateProgress(id_progress_inquiry,"0");

        }
     } );
}
function getRandomInt(max) {
  return Math.floor(Math.random() * max);
}

function prepareResponseForAnwser(data) {
        var message='';
        var rIndex=getRandomInt(messages.chat_bot_answer_template.length);
        message=fillMessage(messages.chat_bot_answer_template[rIndex], data.answer);
        sendChatBotMessage(message);
}
//######################################################
//            Script per Assistente Vocale             #
//######################################################
function analyzeCommand(command) {
      console.log("analiyeCommand");
     $.ajax( {
       url: '/analyzeCommand?command='+command,
       headers: {
               'Access-Control-Allow-Origin': '*',
       },
       type: 'GET',
       processData: false,
       contentType: false,
       beforeSend: function( xhr ) {
           updateProgress(id_progress_analyzeCommand,"0",true);
       },
       success: function(data){
                  updateProgress(id_progress_analyzeCommand,"100");
                  // Cancellazione di una riga
                  if (data && (data.action=='del' || data.action=='delete')  ) {
                    deleteAbsenceById('absence_id'+data.id);
                    showToast("info",messages.action_deleted_id+data.id);
                  // Azione Non riconosciuta
                  } else if (data && data.action=='und') {
                    showToast("info",messages.action_not_recogn);
                  }
                  else {
                    // Aggiorna template handlebars
                    pushHandlebarsTemplate(data,'absence_row')
                  }

       },
       error: function (jqXHR, exception) {
            var msg = '';
            if (jqXHR.status === 0) {
                msg = messages.error_not_connect;
            } else if (jqXHR.status == 404) {
                msg = messages.error_not_found;
            } else if (jqXHR.status == 500) {
                msg = messages.error_server;
            } else if (exception === 'parsererror') {
                msg = messages.error_json_not_parsed;
            } else if (exception === 'timeout') {
                msg = messages.error_time_out;
            } else if (exception === 'abort') {
                msg = messages.error_ajax_aborted;
            } else {
                msg = 'Uncaught Error.\n' + jqXHR.responseText;
            }
            showToast("Error", msg, 3000);
        },
        complete: function(data) {
           updateProgress(id_progress_analyzeCommand,"0");
        }
     } );
}

function showToast(title, message, delay) {
    var myToast = document.getElementById('myToast');
    document.getElementById('toastTitle').innerText = title;
    document.getElementById('toastBody').innerText = message;
    myToast.setAttribute('data-delay', delay);

    var toast = new bootstrap.Toast(myToast);
    toast.show();
}
function deleteAbsenceById(id) {
      var elem = document.getElementById(id);
      return elem.parentNode.removeChild(elem);
}
