// Timeline with agent's thinking (Agent perspective)
// Shows internal reasoning and decision-making process

MATCH (a:Agent {agent_id: 'Agent_Proof_Generator_4'})-[:LOGGED]->(e:Episode)
WHERE e.session_id = $session_id  // Optional filter by session
RETURN
  e.type AS event_type,
  e.timestamp AS when,
  e.content AS what_happened,
  e.thinking AS internal_reasoning,  // Agent's thoughts
  e.session_id AS session
ORDER BY e.timestamp
