// Observable timeline only (External perspective)
// What others can see - no internal thinking

MATCH (e:Episode)
WHERE e.session_id = $session_id
  AND exists((a:Agent {agent_id: 'Agent_Proof_Generator_4'})-[:LOGGED]->(e))
RETURN
  e.type AS event_type,
  e.timestamp AS when,
  e.content AS observable_action,
  e.session_id AS session
ORDER BY e.timestamp
