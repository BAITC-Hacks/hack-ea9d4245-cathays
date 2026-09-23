import {useEffect,useState} from "react";
import {createConversation,sendText,Turn} from "../../api/client";
export function CustomerConversation({onTurn}:{onTurn:(t:Turn)=>void}){
 const [id,setId]=useState(""),[text,setText]=useState(""),[busy,setBusy]=useState(false),[error,setError]=useState("");
 useEffect(()=>{createConversation().then(x=>setId(x.conversation_id)).catch(e=>setError(String(e)))},[]);
 async function submit(){if(!text.trim()||busy)return;setBusy(true);setError("");try{const t=await sendText(id,text);onTurn(t);setText("")}catch(e){setError("Не удалось обработать запрос. Повторите или используйте текст.")}finally{setBusy(false)}}
 return <section><h1>Saqta Voice Router</h1><p>{busy?"Обработка…":"Текстовый режим"}</p><textarea aria-label="Customer message" value={text} onChange={e=>setText(e.target.value)} /><button disabled={busy||!id} onClick={submit}>Отправить</button><button disabled title="Voice adapter is enabled after STT provider configuration">Микрофон</button>{error&&<p role="alert">{error}</p>}</section>
}
