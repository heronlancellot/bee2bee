"""
Intelligence Communication Protocol
This protocol enables sophisticated communication between agents with support for:
- Query/Response patterns
- Knowledge sharing
- Collaborative analysis
- Broadcast messaging
"""

from uagents import Context, Model, Protocol
from typing import Optional, List
from enum import Enum


class MessageType(str, Enum):
    """Types of messages that can be exchanged"""
    QUERY = "query"
    RESPONSE = "response"
    KNOWLEDGE_SHARE = "knowledge_share"
    ANALYSIS_REQUEST = "analysis_request"
    ANALYSIS_RESULT = "analysis_result"
    BROADCAST = "broadcast"
    ACK = "acknowledgment"


class QueryMessage(Model):
    """Request for information or analysis"""
    message_id: str
    query: str
    context: Optional[str] = None
    sender_name: str
    message_type: MessageType = MessageType.QUERY


class ResponseMessage(Model):
    """Response to a query"""
    message_id: str
    original_query_id: str
    response: str
    sender_name: str
    confidence: Optional[float] = None
    message_type: MessageType = MessageType.RESPONSE


class KnowledgeShare(Model):
    """Share knowledge or insights with other agents"""
    message_id: str
    topic: str
    content: str
    sender_name: str
    tags: Optional[List[str]] = []
    message_type: MessageType = MessageType.KNOWLEDGE_SHARE


class AnalysisRequest(Model):
    """Request for collaborative analysis"""
    message_id: str
    data: str
    analysis_type: str
    sender_name: str
    priority: Optional[str] = "normal"
    message_type: MessageType = MessageType.ANALYSIS_REQUEST


class AnalysisResult(Model):
    """Result of analysis"""
    message_id: str
    request_id: str
    findings: str
    sender_name: str
    recommendations: Optional[str] = None
    message_type: MessageType = MessageType.ANALYSIS_RESULT


class BroadcastMessage(Model):
    """Broadcast message to all agents"""
    message_id: str
    content: str
    sender_name: str
    priority: Optional[str] = "normal"
    message_type: MessageType = MessageType.BROADCAST


class AckMessage(Model):
    """Acknowledgment of received message"""
    message_id: str
    original_message_id: str
    sender_name: str
    status: str
    message_type: MessageType = MessageType.ACK


# Create the intelligence protocol
intelligence_proto = Protocol(name="intelligence", version="1.0")


@intelligence_proto.on_message(model=QueryMessage, replies={ResponseMessage, AckMessage})
async def handle_query(ctx: Context, sender: str, msg: QueryMessage):
    """Handle incoming queries from other agents"""
    ctx.logger.info(f"[{ctx.agent.name}] Received query from {msg.sender_name}: {msg.query}")

    # Store the query for processing
    query_key = f"query_{msg.message_id}"
    ctx.storage.set(query_key, {
        "sender": sender,
        "sender_name": msg.sender_name,
        "query": msg.query,
        "context": msg.context,
        "message_id": msg.message_id
    })

    # Send acknowledgment
    await ctx.send(
        sender,
        AckMessage(
            message_id=f"ack_{msg.message_id}",
            original_message_id=msg.message_id,
            sender_name=ctx.agent.name,
            status="received"
        )
    )

    ctx.logger.info(f"[{ctx.agent.name}] Query stored and acknowledged")


@intelligence_proto.on_message(model=ResponseMessage, replies={AckMessage})
async def handle_response(ctx: Context, sender: str, msg: ResponseMessage):
    """Handle responses from other agents"""
    ctx.logger.info(f"[{ctx.agent.name}] Received response from {msg.sender_name}")

    # Store the response
    response_key = f"response_{msg.message_id}"
    ctx.storage.set(response_key, {
        "sender": sender,
        "sender_name": msg.sender_name,
        "response": msg.response,
        "original_query_id": msg.original_query_id,
        "confidence": msg.confidence
    })

    # Send acknowledgment
    await ctx.send(
        sender,
        AckMessage(
            message_id=f"ack_{msg.message_id}",
            original_message_id=msg.message_id,
            sender_name=ctx.agent.name,
            status="received"
        )
    )

    ctx.logger.info(f"[{ctx.agent.name}] Response stored")


@intelligence_proto.on_message(model=KnowledgeShare, replies={AckMessage})
async def handle_knowledge_share(ctx: Context, sender: str, msg: KnowledgeShare):
    """Handle knowledge sharing from other agents"""
    ctx.logger.info(f"[{ctx.agent.name}] Received knowledge from {msg.sender_name}: {msg.topic}")

    # Store the shared knowledge
    knowledge_key = f"knowledge_{msg.message_id}"
    ctx.storage.set(knowledge_key, {
        "sender": sender,
        "sender_name": msg.sender_name,
        "topic": msg.topic,
        "content": msg.content,
        "tags": msg.tags
    })

    # Send acknowledgment
    await ctx.send(
        sender,
        AckMessage(
            message_id=f"ack_{msg.message_id}",
            original_message_id=msg.message_id,
            sender_name=ctx.agent.name,
            status="knowledge_received"
        )
    )

    ctx.logger.info(f"[{ctx.agent.name}] Knowledge stored")


@intelligence_proto.on_message(model=AnalysisRequest, replies={AnalysisResult, AckMessage})
async def handle_analysis_request(ctx: Context, sender: str, msg: AnalysisRequest):
    """Handle analysis requests from other agents"""
    ctx.logger.info(f"[{ctx.agent.name}] Received analysis request from {msg.sender_name}")

    # Store the analysis request
    analysis_key = f"analysis_request_{msg.message_id}"
    ctx.storage.set(analysis_key, {
        "sender": sender,
        "sender_name": msg.sender_name,
        "data": msg.data,
        "analysis_type": msg.analysis_type,
        "priority": msg.priority,
        "message_id": msg.message_id
    })

    # Send acknowledgment
    await ctx.send(
        sender,
        AckMessage(
            message_id=f"ack_{msg.message_id}",
            original_message_id=msg.message_id,
            sender_name=ctx.agent.name,
            status="analysis_queued"
        )
    )

    ctx.logger.info(f"[{ctx.agent.name}] Analysis request queued")


@intelligence_proto.on_message(model=AnalysisResult, replies={AckMessage})
async def handle_analysis_result(ctx: Context, sender: str, msg: AnalysisResult):
    """Handle analysis results from other agents"""
    ctx.logger.info(f"[{ctx.agent.name}] Received analysis result from {msg.sender_name}")

    # Store the analysis result
    result_key = f"analysis_result_{msg.message_id}"
    ctx.storage.set(result_key, {
        "sender": sender,
        "sender_name": msg.sender_name,
        "request_id": msg.request_id,
        "findings": msg.findings,
        "recommendations": msg.recommendations
    })

    # Send acknowledgment
    await ctx.send(
        sender,
        AckMessage(
            message_id=f"ack_{msg.message_id}",
            original_message_id=msg.message_id,
            sender_name=ctx.agent.name,
            status="result_received"
        )
    )

    ctx.logger.info(f"[{ctx.agent.name}] Analysis result stored")


@intelligence_proto.on_message(model=BroadcastMessage, replies={AckMessage})
async def handle_broadcast(ctx: Context, sender: str, msg: BroadcastMessage):
    """Handle broadcast messages from other agents"""
    ctx.logger.info(f"[{ctx.agent.name}] Received broadcast from {msg.sender_name}: {msg.content}")

    # Store the broadcast message
    broadcast_key = f"broadcast_{msg.message_id}"
    ctx.storage.set(broadcast_key, {
        "sender": sender,
        "sender_name": msg.sender_name,
        "content": msg.content,
        "priority": msg.priority
    })

    # Send acknowledgment
    await ctx.send(
        sender,
        AckMessage(
            message_id=f"ack_{msg.message_id}",
            original_message_id=msg.message_id,
            sender_name=ctx.agent.name,
            status="broadcast_received"
        )
    )

    ctx.logger.info(f"[{ctx.agent.name}] Broadcast message stored")


@intelligence_proto.on_message(model=AckMessage)
async def handle_acknowledgment(ctx: Context, sender: str, msg: AckMessage):
    """Handle acknowledgment messages"""
    ctx.logger.info(f"[{ctx.agent.name}] Received ACK from {msg.sender_name} - Status: {msg.status}")

    # Store acknowledgment
    ack_key = f"ack_{msg.original_message_id}"
    ctx.storage.set(ack_key, {
        "sender": sender,
        "sender_name": msg.sender_name,
        "status": msg.status,
        "message_id": msg.message_id
    })
