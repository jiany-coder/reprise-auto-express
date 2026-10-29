(function(){
  var b=document.querySelector('.burger'),n=document.getElementById('nav');
  if(b&&n){
    b.addEventListener('click',function(){var o=n.classList.toggle('open');b.setAttribute('aria-expanded',o?'true':'false');});
    n.addEventListener('click',function(e){if(e.target.tagName==='A'){n.classList.remove('open');b.setAttribute('aria-expanded','false');}});
  }
  var f=document.getElementById('est-form'); if(!f) return;
  var EMAIL=document.documentElement.getAttribute('data-email')||'';
  f.addEventListener('submit',function(e){
    e.preventDefault();
    var m=document.getElementById('est-msg'); m.hidden=false;
    var req=f.querySelectorAll('[required]'),ok=true;
    req.forEach(function(i){ if(!i.value.trim()){ok=false;i.style.borderColor='#e11d2a';} else {i.style.borderColor='';} });
    if(!ok){m.textContent='Merci de remplir les champs obligatoires.';return;}
    var d=new FormData(f),lines=[],obj={};
    d.forEach(function(v,k){lines.push(k+' : '+v);obj[k]=v;});
    if(!EMAIL){m.textContent='Le formulaire sera relié à la boîte de réception de l’entreprise avant la mise en ligne.';return;}
    obj._subject='Nouvelle demande d’estimation – Reprise Auto Express';
    obj._captcha='false'; obj._template='table'; obj._replyto=obj['e-mail']||'';
    var btn=f.querySelector('button[type=submit],input[type=submit]'); if(btn) btn.disabled=true;
    m.textContent='Envoi en cours…';
    fetch('https://formsubmit.co/ajax/'+EMAIL,{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(obj)})
      .then(function(r){return r.json();})
      .then(function(j){
        if(j&&(j.success===true||j.success==='true')){m.textContent='Merci ! Votre demande est bien envoyée, un conseiller vous recontacte rapidement.';f.reset();}
        else{throw new Error('fail');}
      })
      .catch(function(){
        m.innerHTML='L’envoi automatique a échoué. Écrivez-nous directement : <a href="mailto:'+EMAIL+'?subject='+encodeURIComponent('Demande d’estimation')+'&body='+encodeURIComponent(lines.join('\n'))+'">'+EMAIL+'</a>';
      })
      .then(function(){ if(btn) btn.disabled=false; });
  });
})();
