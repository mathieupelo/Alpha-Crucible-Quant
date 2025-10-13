/**
 * Universe Manager Page
 * Manage universes and their ticker compositions
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Skeleton,
  Chip,
  Tooltip,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Group as GroupIcon,
  Edit as EditIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';

import { universeApi } from '@/services/api';
import { Universe, UniverseCreateRequest, UniverseUpdateRequest } from '@/types';
import Logo from '@/components/common/Logo';

const UniverseManager: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  // State for dialogs
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedUniverse, setSelectedUniverse] = useState<Universe | null>(null);
  
  // Form state
  const [universeName, setUniverseName] = useState('');
  const [universeDescription, setUniverseDescription] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Fetch universes
  const {
    data: universesData,
    isLoading,
    error: fetchError,
  } = useQuery('universes', universeApi.getUniverses);

  // Create universe mutation
  const createUniverseMutation = useMutation(universeApi.createUniverse, {
    onSuccess: () => {
      queryClient.invalidateQueries('universes');
      setCreateDialogOpen(false);
      setUniverseName('');
      setUniverseDescription('');
      setError(null);
      setSuccessMessage('Universe created successfully!');
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Failed to create universe');
    },
  });

  // Update universe mutation
  const updateUniverseMutation = useMutation(
    ({ universeId, request }: { universeId: number; request: UniverseUpdateRequest }) =>
      universeApi.updateUniverse(universeId, request),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('universes');
        setEditDialogOpen(false);
        setUniverseName('');
        setUniverseDescription('');
        setError(null);
        setSuccessMessage('Universe updated successfully!');
      },
      onError: (error: any) => {
        setError(error.response?.data?.detail || 'Failed to update universe');
      },
    }
  );

  // Delete universe mutation
  const deleteUniverseMutation = useMutation(universeApi.deleteUniverse, {
    onSuccess: () => {
      queryClient.invalidateQueries('universes');
      setDeleteDialogOpen(false);
      setSelectedUniverse(null);
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Failed to delete universe');
    },
  });

  const handleCreateUniverse = () => {
    if (!universeName.trim()) {
      setError('Universe name is required');
      return;
    }

    const request: UniverseCreateRequest = {
      name: universeName.trim(),
      description: universeDescription.trim() || undefined,
    };

    createUniverseMutation.mutate(request);
  };

  const handleUpdateUniverse = () => {
    if (!selectedUniverse) return;
    
    if (!universeName.trim()) {
      setError('Universe name is required');
      return;
    }

    const request: UniverseUpdateRequest = {
      name: universeName.trim(),
      description: universeDescription.trim() || undefined,
    };

    updateUniverseMutation.mutate({
      universeId: selectedUniverse.id,
      request
    });
  };

  const handleDeleteUniverse = () => {
    if (selectedUniverse) {
      deleteUniverseMutation.mutate(selectedUniverse.id);
    }
  };

  const handleViewUniverse = (universe: Universe) => {
    navigate(`/universes/${universe.id}`);
  };

  const handleOpenEditDialog = (universe: Universe) => {
    setSelectedUniverse(universe);
    setUniverseName(universe.name);
    setUniverseDescription(universe.description || '');
    setError(null);
    setEditDialogOpen(true);
  };

  const handleOpenDeleteDialog = (universe: Universe) => {
    setSelectedUniverse(universe);
    setDeleteDialogOpen(true);
  };

  const handleCloseDialogs = () => {
    setCreateDialogOpen(false);
    setEditDialogOpen(false);
    setDeleteDialogOpen(false);
    setSelectedUniverse(null);
    setUniverseName('');
    setUniverseDescription('');
    setError(null);
    setSuccessMessage(null);
  };

  if (fetchError) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        Failed to load universes. Please check your connection and try again.
      </Alert>
    );
  }

  return (
    <Box>
      {/* Success Message */}
      {successMessage && (
        <Alert 
          severity="success" 
          sx={{ mb: 2 }} 
          onClose={() => setSuccessMessage(null)}
        >
          {successMessage}
        </Alert>
      )}

      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Logo size="medium" showText={false} clickable={true} />
            <Typography variant="h4" component="h1" sx={{ fontWeight: 700 }}>
              Universe Manager
            </Typography>
          </Box>
          <Typography variant="body1" color="text.secondary">
            Create and manage universes of tickers for your trading strategies
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateDialogOpen(true)}
          size="large"
        >
          Create Universe
        </Button>
      </Box>

      {/* Universes Grid */}
      {isLoading ? (
        <Grid container spacing={3}>
          {[...Array(6)].map((_, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card>
                <CardContent>
                  <Skeleton variant="text" height={32} />
                  <Skeleton variant="text" height={24} sx={{ mb: 2 }} />
                  <Skeleton variant="rectangular" height={40} />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      ) : (
        <Grid container spacing={3}>
          {universesData?.universes.map((universe) => (
            <Grid item xs={12} sm={6} md={4} key={universe.id}>
              <Card
                sx={{
                  height: '100%',
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-2px)',
                    boxShadow: 4,
                  },
                }}
              >
                <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  {/* Universe Header */}
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="h6" component="h2" gutterBottom sx={{ fontWeight: 600 }}>
                        {universe.name}
                      </Typography>
                      {universe.description && (
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                          {universe.description}
                        </Typography>
                      )}
                    </Box>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Tooltip title="Edit Universe">
                        <IconButton
                          size="small"
                          onClick={() => handleOpenEditDialog(universe)}
                          color="primary"
                        >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="View Details">
                        <IconButton
                          size="small"
                          onClick={() => handleViewUniverse(universe)}
                          color="primary"
                        >
                          <ViewIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete Universe">
                        <IconButton
                          size="small"
                          onClick={() => handleOpenDeleteDialog(universe)}
                          color="error"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </Box>

                  {/* Universe Stats */}
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <Chip
                      icon={<GroupIcon />}
                      label={`${universe.ticker_count} tickers`}
                      color="primary"
                      variant="outlined"
                      size="small"
                    />
                    <Typography variant="caption" color="text.secondary">
                      Created {new Date(universe.created_at).toLocaleDateString()}
                    </Typography>
                  </Box>

                  {/* Action Button */}
                  <Button
                    variant="outlined"
                    fullWidth
                    onClick={() => handleViewUniverse(universe)}
                    sx={{ mt: 'auto' }}
                  >
                    Manage Tickers
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Empty State */}
      {!isLoading && universesData?.universes.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <GroupIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No universes found
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Create your first universe to start managing tickers for your trading strategies
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
          >
            Create Universe
          </Button>
        </Box>
      )}

      {/* Create Universe Dialog */}
      <Dialog open={createDialogOpen} onClose={handleCloseDialogs} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Universe</DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          <TextField
            autoFocus
            margin="dense"
            label="Universe Name"
            fullWidth
            variant="outlined"
            value={universeName}
            onChange={(e) => setUniverseName(e.target.value)}
            sx={{ mb: 2 }}
            error={!!error && !universeName.trim()}
            helperText={error && !universeName.trim() ? 'Universe name is required' : ''}
          />
          <TextField
            margin="dense"
            label="Description (Optional)"
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            value={universeDescription}
            onChange={(e) => setUniverseDescription(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialogs}>Cancel</Button>
          <Button
            onClick={handleCreateUniverse}
            variant="contained"
            disabled={createUniverseMutation.isLoading}
          >
            {createUniverseMutation.isLoading ? 'Creating...' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Universe Dialog */}
      <Dialog open={editDialogOpen} onClose={handleCloseDialogs} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Universe</DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          <TextField
            autoFocus
            margin="dense"
            label="Universe Name"
            fullWidth
            variant="outlined"
            value={universeName}
            onChange={(e) => setUniverseName(e.target.value)}
            sx={{ mb: 2 }}
            error={!!error && !universeName.trim()}
            helperText={error && !universeName.trim() ? 'Universe name is required' : ''}
          />
          <TextField
            margin="dense"
            label="Description (Optional)"
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            value={universeDescription}
            onChange={(e) => setUniverseDescription(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialogs}>Cancel</Button>
          <Button
            onClick={handleUpdateUniverse}
            variant="contained"
            disabled={updateUniverseMutation.isLoading}
          >
            {updateUniverseMutation.isLoading ? 'Saving...' : 'Save Changes'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Universe Dialog */}
      <Dialog open={deleteDialogOpen} onClose={handleCloseDialogs}>
        <DialogTitle>Delete Universe</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the universe "{selectedUniverse?.name}"? 
            This action cannot be undone and will remove all associated tickers.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialogs}>Cancel</Button>
          <Button
            onClick={handleDeleteUniverse}
            color="error"
            variant="contained"
            disabled={deleteUniverseMutation.isLoading}
          >
            {deleteUniverseMutation.isLoading ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default UniverseManager;
