import React, { useState } from 'react';
import { Modal, Input, Button, Alert } from '../ui';
import { api } from '@/lib/api';

interface CreateTeamModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: () => void;
}

export function CreateTeamModal({ isOpen, onClose, onSuccess }: CreateTeamModalProps) {
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            await api.createTeam(name, description || undefined);

            onSuccess();
            onClose();

            setName('');
            setDescription('');
        } catch (err: unknown) {
            const error = err as { response?: { data?: { detail?: string } } };

            setError(error.response?.data?.detail || 'Failed to create team');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Create a Team">
            <form onSubmit={handleSubmit} className="space-y-4">
                {error && <Alert type="error">{error}</Alert>}

                <Alert type="info">
                    Creating a team locks you in for <strong>60 days</strong>. Choose wisely!
                </Alert>

                <Input
                    label="Team Name"
                    placeholder="The Phantom Seekers"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                    minLength={3}
                    maxLength={100}
                />

                <div>
                    <label className="block text-sm font-medium text-mist-300 mb-2">
                        Description (optional)
                    </label>
                    <textarea
                        className="w-full px-4 py-3 bg-void-200 border border-phantom-900/30 rounded-lg text-mist-100 placeholder:text-mist-600 focus:outline-none focus:border-phantom-600 focus:ring-1 focus:ring-phantom-600 transition-colors resize-none"
                        rows={3}
                        placeholder="Tell others about your team..."
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        maxLength={500}
                    />
                </div>

                <div className="flex justify-end gap-3 pt-4">
                    <Button type="button" variant="secondary" onClick={onClose}>
                        Cancel
                    </Button>
                    <Button type="submit" variant="primary" loading={loading}>
                        Create Team
                    </Button>
                </div>
            </form>
        </Modal>
    );
}
