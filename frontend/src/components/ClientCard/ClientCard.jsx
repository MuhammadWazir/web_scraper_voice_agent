import React from 'react';
import { useNavigate } from 'react-router-dom';
import './ClientCard.css';

function ClientCard({ client }) {
  const navigate = useNavigate();

  const prompts = client?.prompts;
  const areAllPromptsNull = !prompts || Object.values(prompts).every((v) => v === null || v === undefined);
  const isGenerating = areAllPromptsNull;

  const handleClick = (e) => {
    if (isGenerating) {
      e.preventDefault();
      e.stopPropagation();
      return;
    }
    navigate(`/client/${client.client_id}`);
  };

  return (
    <div className={`client-card ${isGenerating ? 'generating' : ''}`} onClick={handleClick}>
      <div className="client-card-header">
        <h3>{client.company_name || 'Unknown Company'}</h3>
      </div>
      <div className="client-card-body">
        <p className="client-url">
          <strong>URL:</strong> {client.request?.website_url || 'N/A'}
        </p>
        <p className="client-audience">
          <strong>Audience:</strong> {client.request?.target_audience || 'N/A'}
        </p>
        {isGenerating && (
          <div className="generating-status">
            <span className="spinner"></span>
            <p>Generating prompts for {client.company_name}...</p>
          </div>
        )}
      </div>
      <div className="client-card-footer">
        <button className="view-btn" disabled={isGenerating}>
          {isGenerating ? 'Generating...' : 'View Agent →'}
        </button>
      </div>
    </div>
  );
}

export default ClientCard;

