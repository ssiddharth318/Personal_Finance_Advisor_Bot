async function api(url, method='GET', body=null){
  const opts={method,headers:{'Content-Type':'application/json'}};
  if(body) opts.body=JSON.stringify(body);
  const r=await fetch(url,opts);
  const data=await r.json();
  if(!r.ok) throw new Error(data.error||'Request failed');
  return data;
}
function money(n){return '₹'+Number(n||0).toLocaleString('en-IN',{maximumFractionDigits:0})}
async function resetDemo(){if(confirm('Reset the dashboard to sample demo data?')){await api('/api/reset-demo','POST');location.reload()}}
