import React from 'react';
import { useNavigate } from 'react-router-dom';
import './ClientCard.css';

function ClientCard({ client }) {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/client/${client.client_id}`);
  };

  return (
    <div className="client-card" onClick={handleClick}>
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
      </div>
      <div className="client-card-footer">
        <button className="view-btn">View Agent →</button>
      </div>
    </div>
  );
}

export default ClientCard;

