import { cleanup, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { saveSession } from '../auth/session';
import { VantagemList } from './VantagemList';

const mocks = vi.hoisted(() => ({ minhas: vi.fn() }));
vi.mock('../services/vantagemService', () => ({
  vantagemService: {
    minhas: mocks.minhas,
    ativar: vi.fn(), desativar: vi.fn(), excluir: vi.fn(),
  },
}));

describe('gerenciamento mostra apenas vantagens próprias', () => {
  beforeEach(() => {
    sessionStorage.clear();
    saveSession({ access_token: 'company-jwt', id: 10, nome: 'Empresa A', tipo: 'EMPRESA' });
    mocks.minhas.mockResolvedValue([
      { id: 1, empresa_id: 10, empresa_nome: 'Empresa A', nome: 'Oferta própria', descricao: 'Descrição', custo: '10.00', imagem_url: null, ativa: true },
      { id: 2, empresa_id: 20, empresa_nome: 'Empresa B', nome: 'Oferta alheia', descricao: 'Privada', custo: '12.00', imagem_url: null, ativa: true },
    ]);
  });
  afterEach(() => { cleanup(); vi.clearAllMocks(); sessionStorage.clear(); });

  it('omite registros de outras empresas e não renderiza ações sobre eles', async () => {
    render(<MemoryRouter><VantagemList /></MemoryRouter>);
    expect(await screen.findByText('Oferta própria')).toBeInTheDocument();
    await waitFor(() => expect(screen.queryByText('Oferta alheia')).not.toBeInTheDocument());
    expect(screen.getByRole('link', { name: /Editar/ })).toHaveAttribute('href', '/vantagens/1/editar');
    expect(screen.getAllByRole('button', { name: /Excluir/ })).toHaveLength(1);
  });
});
