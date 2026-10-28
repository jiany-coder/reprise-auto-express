(function(){
  var f=document.getElementById('est-form'); if(!f) return;
  var EMAIL=document.documentElement.getAttribute('data-email')||'';
  f.addEventListener('submit',function(e){
    e.preventDefault();
    var m=document.getElementById('est-msg'); m.hidden=false;
    var req=f.querySelectorAll('[required]'),ok=true;
    req.forEach(function(i){ if(!i.value.trim()){ok=false;i.style.borderColor='#e11d2a';} else {i.style.borderColor='';} });
    if(!ok){m.textContent='Merci de remplir les champs obligatoires.';return;}
    var d=new FormData(f),lines=[];
    d.forEach(function(v,k){lines.push(k+' : '+v);});
    if(EMAIL){
      location.href='mailto:'+EMAIL+'?subject='+encodeURIComponent('Demande d’estimation')+'&body='+encodeURIComponent(lines.join('\n'));
      m.textContent='Votre messagerie va s’ouvrir pour envoyer la demande.';
    } else {
      m.textContent='Le formulaire sera relié à la boîte de réception de l’entreprise avant la mise en ligne.';
    }
  });
})();
