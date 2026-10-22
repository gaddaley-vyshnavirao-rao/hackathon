from __future__ import annotations

import plotly.graph_objects as go

from iaia.models import ModernizationAction


def build_modernization_roadmap(actions: list[ModernizationAction]):
    """Build a milestone timeline and dependency connectors for a modernization plan."""
    phases: list[str] = []
    for action in actions:
        if action.phase not in phases:
            phases.append(action.phase)
    positions = {phase: index for index, phase in enumerate(phases)}
    figure = go.Figure()

    figure.add_trace(go.Scatter(
        x=list(range(len(phases))),
        y=[0] * len(phases),
        mode='markers+text',
        text=phases,
        textposition='top center',
        marker={'size': 18, 'color': '#2563eb'},
        name='Modernization phases',
        hovertemplate='%{text}<extra></extra>',
    ))

    for action in actions:
        source = positions[action.phase]
        for dependency in action.dependencies:
            target_phase = next(
                (candidate.phase for candidate in actions
                 if candidate.title == dependency or candidate.phase == dependency),
                None,
            )
            if target_phase is None or target_phase == action.phase:
                continue
            target = positions[target_phase]
            figure.add_trace(go.Scatter(
                x=[target, source], y=[0, 0], mode='lines+markers',
                line={'color': '#64748b', 'width': 2},
                marker={'size': 7}, name='Dependency',
                hovertemplate=f'{target_phase} -> {action.phase}<extra></extra>',
                showlegend=False,
            ))

    figure.update_layout(
        title='Modernization Roadmap',
        xaxis={'tickmode': 'array', 'tickvals': list(range(len(phases))), 'ticktext': phases, 'showgrid': False},
        yaxis={'visible': False, 'range': [-1, 1]},
        height=300,
        margin={'l': 20, 'r': 20, 't': 60, 'b': 80},
        showlegend=False,
    )
    return figure
