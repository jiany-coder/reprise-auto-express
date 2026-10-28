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
    var d=new FormData(f),lines=[];
    d.forEach(function(v,k){lines.push(k+' : '+v);});
    if(EMAIL){
      location.href='mailto:'+EMAIL+'?subject='+encodeURIComponent('Demande d\u2019estimation')+'&body='+encodeURIComponent(lines.join('\n'));
      m.textContent='Votre messagerie va s\u2019ouvrir pour envoyer la demande.';
    } else {
      m.textContent='Le formulaire sera relié à la boîte de réception de l\u2019entreprise avant la mise en ligne.';
    }
  });
})();
