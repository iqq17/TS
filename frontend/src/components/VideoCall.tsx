import React, { useState, useEffect } from 'react';
import { CallClient, CallAgent, VideoStreamRenderer, LocalVideoStream } from '@azure/communication-calling';
import { AzureCommunicationTokenCredential } from '@azure/communication-common';

interface VideoCallProps {
  token: string;
  groupId: string;
}

const VideoCall: React.FC<VideoCallProps> = ({ token, groupId }) => {
  const [callAgent, setCallAgent] = useState<CallAgent | null>(null);
  const [call, setCall] = useState<Call | null>(null);
  const [localVideoStream, setLocalVideoStream] = useState<LocalVideoStream | null>(null);

  useEffect(() => {
    const init = async () => {
      const callClient = new CallClient();
      const tokenCredential = new AzureCommunicationTokenCredential(token);
      const agent = await callClient.createCallAgent(tokenCredential);
      setCallAgent(agent);

      const stream = new LocalVideoStream();
      setLocalVideoStream(stream);
    };

    init();
  }, [token]);

  const startCall = async () => {
    if (callAgent && localVideoStream) {
      const call = callAgent.join({ groupId }, { videoOptions: { localVideoStreams: [localVideoStream] } });
      setCall(call);

      call.on('remoteParticipantsUpdated', () => {
        // Handle remote participants joining/leaving
      });
    }
  };

  const endCall = () => {
    call?.hangUp();
    setCall(null);
  };

  return (
    <div className="video-call-container">
      <div className="local-video-stream">
        {localVideoStream && <LocalVideoStreamView stream={localVideoStream} />}
      </div>
      <div className="remote-participants">
        {/* Render remote participants here */}
      </div>
      <div className="controls">
        <button onClick={startCall} disabled={!callAgent || call}>Join Call</button>
        <button onClick={endCall} disabled={!call}>End Call</button>
      </div>
    </div>
  );
};

const LocalVideoStreamView: React.FC<{ stream: LocalVideoStream }> = ({ stream }) => {
  const videoRef = React.useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (videoRef.current) {
      const renderer = new VideoStreamRenderer(stream);
      const view = renderer.createView();
      videoRef.current.appendChild(view.target);

      return () => {
        renderer.dispose();
      };
    }
  }, [stream]);

  return <div ref={videoRef} className="video-stream"></div>;
};

export default VideoCall;