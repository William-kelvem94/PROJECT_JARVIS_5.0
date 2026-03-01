import { NextResponse } from 'next/server';
import { AccessToken, type AccessTokenOptions, type VideoGrant } from 'livekit-server-sdk';
import { RoomConfiguration } from '@livekit/protocol';

type ConnectionDetails = {
  serverUrl: string;
  roomName: string;
  participantName: string;
  participantToken: string;
};

// NOTE: you are expected to define the following environment variables in `.env.local`:
const API_KEY = process.env.LIVEKIT_API_KEY;
const API_SECRET = process.env.LIVEKIT_API_SECRET;
const LIVEKIT_URL = process.env.LIVEKIT_URL;

// Forçar execução dinâmica para evitar cache de erros HTML do Next.js 15
export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
  try {
    // 1. Validate Environment
    const missingKeys = [];
    if (!LIVEKIT_URL) missingKeys.push('LIVEKIT_URL');
    if (!API_KEY) missingKeys.push('LIVEKIT_API_KEY');
    if (!API_SECRET) missingKeys.push('LIVEKIT_API_SECRET');

    if (missingKeys.length > 0) {
      console.error(`[API] Missing environment variables: ${missingKeys.join(', ')}`);
      return NextResponse.json(
        { error: `Configuração incompleta: ${missingKeys.join(', ')}` },
        { status: 500 }
      );
    }

    // 2. Parse Body
    let body;
    try {
      body = await req.json();
    } catch (e) {
      body = {};
    }

    const agentName: string = body?.room_config?.agents?.[0]?.agent_name;
    const participantName: string = body?.participant_name || 'Chefe';

    // 3. Generate Token
    const participantIdentity = `jarvis_user_${Date.now()}`;
    const roomName = body?.room_name || `jarvis_room_${Math.floor(Math.random() * 1000)}`;

    const participantToken = await createParticipantToken(
      {
        identity: participantIdentity,
        name: participantName,
        metadata: JSON.stringify({ user_name: participantName })
      },
      roomName,
      agentName
    );

    // 4. Return Data
    const data: ConnectionDetails = {
      serverUrl: LIVEKIT_URL!,
      roomName,
      participantToken: participantToken,
      participantName,
    };

    return NextResponse.json(data, {
      headers: { 'Cache-Control': 'no-store' }
    });
  } catch (error: any) {
    console.error('[API] Connection Error:', error);
    return NextResponse.json(
      { error: 'Erro ao conectar com LiveKit.', details: error.message },
      { status: 500 }
    );
  }
}

function createParticipantToken(
  userInfo: AccessTokenOptions,
  roomName: string,
  agentName?: string
): Promise<string> {
  const at = new AccessToken(API_KEY, API_SECRET, {
    ...userInfo,
    ttl: '15m',
  });
  const grant: VideoGrant = {
    room: roomName,
    roomJoin: true,
    canPublish: true,
    canPublishData: true,
    canSubscribe: true,
  };
  at.addGrant(grant);

  if (agentName) {
    at.roomConfig = new RoomConfiguration({
      agents: [{ agentName }],
    });
  }

  return at.toJwt();
}
