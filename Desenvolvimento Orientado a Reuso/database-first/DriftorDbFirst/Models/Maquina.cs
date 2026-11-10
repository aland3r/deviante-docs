using System;
using System.Collections.Generic;

namespace DriftorDbFirst.Models;

public partial class Maquina
{
    public int Id { get; set; }

    public int EmpresaId { get; set; }

    public string Nome { get; set; }

    public string Tag { get; set; }

    public string Tipo { get; set; }

    public string Situacao { get; set; }

    public DateOnly CriadaEm { get; set; }

    public virtual Empresa Empresa { get; set; }
}
