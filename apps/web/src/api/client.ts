export type Turn={conversation_id:string;turn_id:string;trace_id:string;assistant_message:string;routing:any;execution:any};
const base=import.meta.env.VITE_API_URL ?? "http://localhost:8000";
export async function createConversation(){return (await fetch(`${base}/v1/conversations`,{method:"POST"})).json() as Promise<{conversation_id:string}>}
export async function sendText(id:string,text:string):Promise<Turn>{const r=await fetch(`${base}/v1/conversations/${id}/turns`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text,input_mode:"text",client_turn_id:crypto.randomUUID()})});if(!r.ok)throw new Error(await r.text());return r.json()}
export async function getTrace(conversation:string,turn:string){return (await fetch(`${base}/v1/conversations/${conversation}/traces/${turn}`)).json()}
