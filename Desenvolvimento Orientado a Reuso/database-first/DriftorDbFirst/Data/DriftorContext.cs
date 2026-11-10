using System;
using System.Collections.Generic;
using DriftorDbFirst.Models;
using Microsoft.EntityFrameworkCore;

namespace DriftorDbFirst.Data;

public partial class DriftorContext : DbContext
{
    public DriftorContext(DbContextOptions<DriftorContext> options)
        : base(options)
    {
    }

    public virtual DbSet<Empresa> Empresas { get; set; }

    public virtual DbSet<Maquina> Maquinas { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Empresa>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("empresas_pkey");

            entity.ToTable("empresas", "dbfirst");

            entity.HasIndex(e => e.Cnpj, "empresas_cnpj_key").IsUnique();

            entity.Property(e => e.Id)
                .UseIdentityAlwaysColumn()
                .HasColumnName("id");
            entity.Property(e => e.Cnpj)
                .IsRequired()
                .HasMaxLength(18)
                .HasColumnName("cnpj");
            entity.Property(e => e.Nome)
                .IsRequired()
                .HasMaxLength(80)
                .HasColumnName("nome");
            entity.Property(e => e.Setor)
                .IsRequired()
                .HasMaxLength(60)
                .HasColumnName("setor");
        });

        modelBuilder.Entity<Maquina>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("maquinas_pkey");

            entity.ToTable("maquinas", "dbfirst");

            entity.Property(e => e.Id)
                .UseIdentityAlwaysColumn()
                .HasColumnName("id");
            entity.Property(e => e.CriadaEm)
                .HasDefaultValueSql("CURRENT_DATE")
                .HasColumnName("criada_em");
            entity.Property(e => e.EmpresaId).HasColumnName("empresa_id");
            entity.Property(e => e.Nome)
                .IsRequired()
                .HasMaxLength(80)
                .HasColumnName("nome");
            entity.Property(e => e.Situacao)
                .IsRequired()
                .HasMaxLength(20)
                .HasDefaultValueSql("'ativa'::character varying")
                .HasColumnName("situacao");
            entity.Property(e => e.Tag)
                .IsRequired()
                .HasMaxLength(20)
                .HasColumnName("tag");
            entity.Property(e => e.Tipo)
                .IsRequired()
                .HasMaxLength(40)
                .HasColumnName("tipo");

            entity.HasOne(d => d.Empresa).WithMany(p => p.Maquinas)
                .HasForeignKey(d => d.EmpresaId)
                .OnDelete(DeleteBehavior.ClientSetNull)
                .HasConstraintName("maquinas_empresa_id_fkey");
        });

        OnModelCreatingPartial(modelBuilder);
    }

    partial void OnModelCreatingPartial(ModelBuilder modelBuilder);
}
